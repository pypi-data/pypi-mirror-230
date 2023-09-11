# -*- coding: utf-8 -*-
# @Time    : 2022/10/23 19:00
# @Author  : mf.liang
# @File    : dhcp_pkt.py
# @Software: PyCharm
# @desc    :
import copy
import random
from argparse import Namespace
from ipaddress import ip_address
from time import sleep
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.dhcp6 import DHCP6_Solicit, DHCP6_Release, DHCP6OptClientId, DHCP6OptIA_NA, DHCP6OptIA_PD, \
    DHCP6_Request, DHCP6OptServerId, \
    DHCP6_RelayForward, DUID_LLT, DHCP6_Renew, DHCP6_Decline, DHCP6OptRelayMsg, All_DHCP_Relay_Agents_and_Servers, \
    DHCP6OptIfaceId, DUID_EN, DHCP6_Advertise, DHCP6_Reply
from scapy.layers.inet import UDP, IP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.plist import PacketList
from scapy.utils import str2mac
from scapy.sendrecv import sendp, srp1, AsyncSniffer
from dhcptool.env_args import pkt_result, logs
from dhcptool.options import Dhcp4Options, Dhcp6Options
from dhcptool.tools import Tools
from typing import Union, Optional


class Pkt:

    def __init__(self, args) -> None:
        self.args = args
        self.ether, self.ip, self.ipv6, self.udp, self.bootp = Ether(), IP(), IPv6(), UDP(), BOOTP()
        self.timeout = 200 / 1000
        self.mac = Tools.get_mac(self.args)
        self.xid = Tools.get_xid_by_mac(self.mac)

    def async_sniff(self, async_sniff_args, pkt) -> Optional[PacketList]:
        async_sniff_result = AsyncSniffer(
            iface=self.args.iface, **async_sniff_args) if self.args.iface else AsyncSniffer(**async_sniff_args)
        async_sniff_result.start()
        sleep(10 / 1000)
        sendp(pkt, verbose=0, iface=self.args.iface) if self.args.iface else sendp(pkt, verbose=0)
        async_sniff_result.join()
        return async_sniff_result.results

    def send_dhcp6_pkt(self, pkt) -> Optional[PacketList]:
        """
        发送并接收 dhcp6 数据包
        :param pkt:
        :return:
        """
        assert self.args.filter is None or ip_address(self.args.filter).version == 6
        if self.args.filter:
            filter_args = self.args.filter
        elif self.args.dhcp_server:
            filter_args = self.args.dhcp_server
        else:
            logs.info("v6发包需要指定IPv6服务器")
            filter_args = All_DHCP_Relay_Agents_and_Servers
        Tools.print_formart(pkt, self.args.debug)
        async_sniff_args = {"filter": f'port 547 and src host {filter_args}', "count": 1, "timeout": self.timeout}
        return self.async_sniff(async_sniff_args, pkt)

    def send_dhcp4_pkt(self, pkt) -> Optional[PacketList]:
        """
        发送并接收 dhcp4 数据包
        :param pkt:
        :return:
        """
        if self.args.filter and ip_address(self.args.filter).version == 4:
            Tools.print_formart(pkt, self.args.debug)
            async_sniff_args = {"filter": f'port 67 and src host {self.args.filter}', "count": 1, "timeout": self.timeout}
            response = self.async_sniff(async_sniff_args, pkt)
            return response
        elif self.args.dhcp_server and ip_address(self.args.dhcp_server).version == 4:
            Tools.print_formart(pkt, self.args.debug)
            srp1_args = {"verbose": 0, "timeout": self.timeout}
            response = srp1(pkt, iface=self.args.iface, **srp1_args) if self.args.iface else srp1(pkt, **srp1_args)
            None if response else logs.error('没有接收到返回包！')
            return response
        else:
            logs.info("v4发包需要指定IPv4服务器")


class Dhcp6Pkt(Pkt):

    def __init__(self, args) -> None:
        super(Dhcp6Pkt, self).__init__(args)
        if args.filter:
            self.ipv6.src = self.args.ip_src if self.args.ip_src else Tools.get_local_ipv6()
            self.ipv6.dst = All_DHCP_Relay_Agents_and_Servers
        else:
            self.ipv6.src = self.args.ip_src if self.args.ip_src else Tools.get_local_ipv6()
            self.ipv6.dst = self.args.dhcp_server
        self.ether_ipv6_udp = self.ether / self.ipv6 / self.udp
        self.duid_llt = DUID_LLT(lladdr=self.mac, timeval=self.xid)
        self.duid_en = DUID_EN(enterprisenum=1058949886, id=bytes.fromhex('7db44f928a1d4ef7c842c434'))
        self.solicit = DHCP6_Solicit(trid=self.xid)  # TODO: 将xid修改为 self.xid，影响未知
        self.release = DHCP6_Release(trid=self.xid)
        self.decline = DHCP6_Decline(trid=self.xid)
        self.renew = DHCP6_Renew(trid=self.xid)
        self.opt_client_id = DHCP6OptClientId(duid=self.duid_llt)
        self.opt_ia_na = DHCP6OptIA_NA(iaid=self.xid)
        self.opt_ia_pd = DHCP6OptIA_PD(iaid=self.xid)
        self.request = DHCP6_Request(trid=self.xid)
        self.opt_server_id = DHCP6OptServerId(duid=self.duid_en)
        self.relay_forward = DHCP6_RelayForward(linkaddr=self.args.relay_forward)
        self.make_options = Dhcp6Options(self.args)
        self.options_list = self.make_options.make_options_list()
        self.dhcp6_options = self.make_options.parse_options()

    def make_pkts(self, message_type) -> Union[DHCP6_Solicit, DHCP6_Request, DHCP6_RelayForward]:
        """
        解析并制作报文
        :param message_type: 报文消息类型
        :return:
        """
        pkt_dhcp6 = eval(f'self.{message_type}')
        opt_client_id = self.opt_client_id / self.opt_server_id
        if self.args.single and self.dhcp6_options:
            for option in self.dhcp6_options:
                if int(option[0]) == 5:
                    self.opt_ia_na.ianaopts.append(self.make_options.sub_option_5(addr=option[1]))
                    opt_client_id.add_payload(self.opt_ia_na)
                if int(option[0]) == 26:
                    self.opt_ia_pd.iapdopt.append(self.make_options.sub_option_26(prefix=option[1]))
                    opt_client_id.add_payload(self.opt_ia_pd)
        else:
            if message_type == 'request':
                reply_pkt = pkt_result.get('dhcp6_advertise').get(timeout=self.timeout)
            else:
                reply_pkt = pkt_result.get('dhcp6_reply').get(timeout=self.timeout)
            opt_client_id = reply_pkt[DHCP6OptClientId]

        pkt = self.ether_ipv6_udp / pkt_dhcp6 / opt_client_id / self.options_list
        return pkt

    def dhcp6_solicit(self) -> DHCP6_Solicit:
        """
        制作solicit包
        :return:
        """
        if self.dhcp6_options:
            for option in self.dhcp6_options:
                if int(option[0]) == 5:
                    self.opt_ia_na.ianaopts.append(self.make_options.sub_option_5(addr=option[1]))
                elif int(option[0]) == 26:
                    self.opt_ia_pd.iapdopt.append(self.make_options.sub_option_26(prefix=option[1]))
        # 拼接数据包
        solicit_pkt = self.ether_ipv6_udp / self.solicit / self.opt_client_id
        if not self.args.pd or self.args.na:  # NA
            solicit_pkt.add_payload(self.opt_ia_na)
        if self.args.pd:  # PD
            solicit_pkt.add_payload(self.opt_ia_pd)
        solicit_pkt.add_payload(self.options_list)
        if self.args.dhcp_server:
            solicit_pkt = self.dhcp6_relay_ward(solicit_pkt[DHCP6_Solicit])
            return solicit_pkt
        return solicit_pkt

    def dhcp6_advertise(self) -> DHCP6_Advertise:
        pass

    def dhcp6_request(self) -> DHCP6_Request:
        """
        制作request包
        :return:
        """
        request_pkt = self.make_pkts('request')
        if self.args.dhcp_server:
            request_pkt = self.dhcp6_relay_ward(request_pkt[DHCP6_Request])
            return request_pkt
        return request_pkt

    def dhcp6_reply(self) -> DHCP6_Reply:
        pass

    def dhcp6_renew(self) -> DHCP6_Renew:
        """
        制作renew包
        :return:
        """
        renew_pkt = self.make_pkts('renew')
        if self.args.dhcp_server:
            renew_pkt = self.dhcp6_relay_ward(renew_pkt[DHCP6_Renew])
            return renew_pkt
        return renew_pkt

    def dhcp6_release(self) -> DHCP6_Release:
        """
        制作release包
        :return:
        """
        release_pkt = self.make_pkts('release')
        if self.args.dhcp_server:
            release_pkt = self.dhcp6_relay_ward(release_pkt[DHCP6_Release])
            return release_pkt
        return release_pkt

    def dhcp6_decline(self) -> DHCP6_Decline:
        """
        制作decline包
        :return:
        """
        decline_pkt = self.make_pkts('decline')
        if self.args.dhcp_server:
            decline_pkt = self.dhcp6_relay_ward(decline_pkt[DHCP6_Decline])
            return decline_pkt
        return decline_pkt

    def dhcp6_relay_ward(self, pkt=None) -> DHCP6_RelayForward:
        """
        制作中继包
        :return:
        """
        if pkt.getlayer(DHCP6OptIfaceId):
            face_id_layer = copy.deepcopy(pkt.getlayer(DHCP6OptIfaceId))
            face_id_sub_layer = copy.deepcopy(face_id_layer[1:])
            face_id_layer.remove_payload()
            del pkt[DHCP6OptIfaceId]
            relay_forward_pkt = self.ether_ipv6_udp / self.relay_forward / face_id_layer
            relay_forward_pkt.add_payload(DHCP6OptRelayMsg(message=pkt / face_id_sub_layer))
        else:
            relay_forward_pkt = self.ether_ipv6_udp / self.relay_forward
            relay_forward_pkt.add_payload(DHCP6OptRelayMsg(message=pkt))
        return relay_forward_pkt


class Dhcp4Pkt(Pkt):

    def __init__(self, args: Namespace) -> None:
        super(Dhcp4Pkt, self).__init__(args)

        self.udp.sport, self.udp.dport = 67, 67
        self.bootp.chaddr, self.bootp.xid = self.mac, random.randint(1, 900000000)
        if args.filter:
            self.ether.src, self.ether.dst = str2mac(self.mac), 'ff:ff:ff:ff:ff:ff'
            self.ip.src, self.ip.dst = self.args.ip_src if self.args.ip_src else '0.0.0.0', '255.255.255.255'
            self.is_relay_forward = self.args.relay_forward == Tools.get_local_ipv4()
            self.relay_forward = '0.0.0.0' if self.is_relay_forward else self.args.relay_forward
            self.bootp.flag, self.bootp.giaddr = 1, self.relay_forward
        else:
            self.ip.src, self.ip.dst = self.args.ip_src if self.args.ip_src else None, self.args.dhcp_server
            self.bootp.flag, self.bootp.giaddr = 0, self.args.relay_forward
        self.ether_ip_udp_bootp = self.ether / self.ip / self.udp / self.bootp
        self.make_options = Dhcp4Options(self.args)
        self.options_list = self.make_options.make_options_list()

    def make_pkts(self, message_type, **kwargs) -> DHCP:
        """
        组装  discover/request/decline/inform报文，
        :param message_type: 请求类型
        :return:
        """
        options = [("message-type", message_type)]

        if not self.args.single and message_type != 'discover':

            if message_type == 'request':
                response_pkt = pkt_result.get('dhcp4_offer').get(timeout=self.timeout)
                if kwargs.get('message') == 'exception_request':
                    response_pkt = BOOTP(yiaddr='0.0.0.1')

            else:
                response_pkt = pkt_result.get('dhcp4_ack').get(timeout=self.timeout)

            yiaddr = response_pkt[BOOTP].yiaddr
            options.append(("requested_addr", yiaddr))

        [options.append(i) for i in self.options_list]
        make_pkt = self.ether_ip_udp_bootp / DHCP(options=options)
        return make_pkt

    def dhcp4_discover(self) -> DHCP:
        """
        制作 discover包
        :return:
        """
        discover_pkt = self.make_pkts("discover")
        return discover_pkt

    def dhcp4_offer(self) -> DHCP:
        pass

    def dhcp4_request(self) -> DHCP:
        """
        制作 request包
        :return:
        """
        request_pkt = self.make_pkts('request')
        return request_pkt

    def dhcp4_exception_request(self) -> DHCP:
        """
        制作 一个会回nak的request包
        :return:
        """
        request_pkt = self.make_pkts('request', message='exception_request')
        return request_pkt

    def dhcp4_ack(self) -> DHCP:
        pass

    def dhcp4_decline(self) -> DHCP:
        """
        制作 decline包
        :return:
        """
        decline_pkt = self.make_pkts('decline')
        return decline_pkt

    def dhcp4_release(self) -> DHCP:
        """
        制作 release包
        :return:
        """
        release_pkt = self.make_pkts('release')
        return release_pkt

    def dhcp4_inform(self) -> DHCP:
        """
        制作 inform包
        :return:
        """
        inform_pkt = self.make_pkts('inform')
        return inform_pkt
