from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES

from dbDaemon import Daemon

import argparse
import os
import sys

from analyzer import PacketAnalyzer

db = Daemon()
print("Daemon created\n")
pkt_raw_list = db.read_all_pkt_raw()
pkt_features_list =  db.read_all_pkt_features()

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

# db.close()


