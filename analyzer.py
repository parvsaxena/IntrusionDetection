from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES
import argparse
import os
import sys

# Time ??, Source IP(d), Destination IP(d), Protocol ??, Length(d),
# Source Port(d), Dest Port(d), TTL(d), IP version ??
# https://www.howtoinstall.co/en/ubuntu/xenial/tshark

def expand(x):
    yield x.name
    while x.payload:
        x = x.payload
        yield x.name

def extract_ip(parsed_dict, ip_pkt):
    parsed_dict['ip_src'] = ip_pkt.src
    parsed_dict['ip_dst'] = ip_pkt.dst
    parsed_dict['ip_ttl'] = ip_pkt.ttl
    parsed_dict['ip_len'] = ip_pkt.len
    parsed_dict['ip_ver'] = ip_pkt.version
    # TODO: prototype number to name translation
    parsed_dict['proto'] = ip_pkt.proto

def extract_ether(parsed_dict, ether_pkt):
    parsed_dict['mac_src'] = ether_pkt.src
    parsed_dict['mac_dst'] = ether_pkt.dst
    parsed_dict['ether_type'] = ether_pkt.type
    # https://github.com/secdev/scapy/blob/master/scapy/libs/ethertypes.py
    # print(ETHER_TYPES['IPV4'])

def extract_tcp(parsed_dict, tcp_pkt):
    parsed_dict['src_port'] = tcp_pkt.sport
    parsed_dict['dst_port'] = tcp_pkt.dport

def extract_udp(parsed_dict, udp_pkt):
    parsed_dict['src_port'] = udp_pkt.sport
    parsed_dict['dst_port'] = udp_pkt.dport
    parsed_dict['udp_len'] = udp_pkt.len

def extract_icmp(parsed_dict, icmp_pkt):
    print(icmp_pkt.summary())
    # TODO: Ask which more fields are necessary
    parsed_dict['icmp_type'] = icmp_pkt.type  # 0 for request, 8 for reply
    parsed_dict['icmp_type_str'] = icmptypes[icmp_pkt.type]
    parsed_dict['icmp_code'] = icmp_pkt.code  # code field which gives extra information about icmp type
    
def extract_arp(parsed_dict, arp_pkt):
    print(arp_pkt.summary())
    parsed_dict['arp_op'] = arp_pkt.op # 1 who-has, 2 is-at
    parsed_dict['arp_psrc'] = arp_pkt.psrc
    parsed_dict['arp_pdst'] = arp_pkt.pdst
    parsed_dict['arp_hwsrc'] = arp_pkt.hwsrc
    parsed_dict['arp_hwdst'] = arp_pkt.hwdst

def parse_packet(pkt_data):
    
    print(type(pkt_data))
    # pkt_data = Ether(pkt_data)
    print(list(expand(pkt_data)))   
    #print(ip_pkt.show())
    # TODO: Initialize data
    parsed_dict = {}
    # print(tape(ip_pkt))
    if pkt_data.haslayer(Ether):
        print("Ether layer exists")
        ether_pkt = pkt_data.getlayer(Ether)
        extract_ether(parsed_dict, ether_pkt)
    # TODO: Extract ports
    # TODO: Do we need IPv6 support?
    # IP packet
    if pkt_data.haslayer(IP):
        print("Received IP packet")
        ip_pkt = pkt_data.getlayer(IP)
        extract_ip(parsed_dict, ip_pkt)
        # print(ip_pkt.show())
 
    if pkt_data.haslayer(TCP):
        print("TCP layer exists")
        tcp_pkt = pkt_data.getlayer(TCP)
        extract_tcp(parsed_dict, tcp_pkt)

    if pkt_data.haslayer(UDP):
        udp_pkt = pkt_data.getlayer(UDP)
        extract_udp(parsed_dict, udp_pkt)

        print("UDP layer exists")
    if pkt_data.haslayer(ARP):
        print("ARP layer exists")
        arp_pkt = pkt_data.getlayer(ARP)
        extract_arp(parsed_dict, arp_pkt)
    if pkt_data.haslayer(ICMP):
        icmp_pkt = pkt_data.getlayer(ICMP)
        extract_icmp(parsed_dict, icmp_pkt)

        print("ICMP layer exists")

    print("Dictionary\n", parsed_dict)
    print(pkt_data.summary())
    return



count = 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pcap analyzer')
    parser.add_argument('--pcap', help="provide pcap to analyze", required=True)
    args = parser.parse_args()
    for pkt_data, pkt_metadata in RawPcapReader(args.pcap):
        count = count + 1
        print("Packet no ", count)
        # print(pkt_metadata)
        # print(pkt_data)
        print(type(pkt_data))
        parse_packet(Ether(pkt_data))
