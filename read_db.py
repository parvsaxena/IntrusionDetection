from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES

from dbDaemon import Daemon

import argparse
import os
import sys

from analyzer import parse_packet

db =Daemon()

pkt = db.read_one_pkt()
if pkt is not None:
    print("Reading one dump")
    print(pkt)
    print(Ether(pkt[2]).summary())
    print(parse_packet(Ether(pkt[2])))
else:
    print ("COuldnt read anything")

db.close()


