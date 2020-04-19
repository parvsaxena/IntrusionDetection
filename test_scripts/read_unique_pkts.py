from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES

from dbDaemon import dbDriver

import argparse
import os
import sys

from analyzer import PacketAnalyzer, parse_packet

def write(pkt):
    wrpcap('length_pkt.pcap', iter(pkt), append=True)  #appends packet to output file   


db = dbDriver("scada")
pkt_analyzer = PacketAnalyzer(False)

print("Daemon created\n")
# pkt_raw_list = db.read_all_pkt_raw()
# pkt_features_list =  db.read_all_pkt_features()

id_list = [2]
pkt_raw_list = []
# fp = fopen('length_pkt.pcap')

for id in id_list:
    pkt_raw = db.read_raw_by_id(id)
    print (parse_packet(Ether(pkt_raw[2])))
    pkt_raw_list.append(pkt_raw[2])
    eth_pkt = Ether(pkt_raw[2])
    eth_pkt.show()
    print("IP chk", eth_pkt[IP].chksum)
    print(eth_pkt[UDP].chksum)
    
    #CHange IP
    eth_pkt[IP].dst = "128.220.221.16"
    # Recompute chksum
    del eth_pkt[IP].chksum
    del eth_pkt[UDP].chksum
    eth_pkt.show2(dump=False)
    
    # sendp(eth_pkt, iface='eth2', count = 100, return_packets = True)

# Write the list to pcap
write(pkt_raw_list)


# def write(pkt):
#     wrpcap('length_pkt.pcap', pkt, append=True)  #appends packet to output file   
"""
for pkt_raw in pkt_raw_list:
    print("Reading one dump\n")
    print(pkt_raw)
    print(Ether(pkt_raw[2]).summary())
    pkt_analyzer = PacketAnalyzer(False)
    print(pkt_analyzer.parse_packet(Ether(pkt_raw[2]), False))

for pkt_raw in pkt_features_list:
    print("Reading one dump\n")
    print(pkt_raw)
    
    #print(Ether(pkt_raw[2]).summary())
    #pkt_analyzer = PacketAnalyzer(False)
    #print(pkt_analyzer.parse_packet(Ether(pkt_raw[2]), False))
"""
# db.close()

