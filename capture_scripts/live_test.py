import sys
sys.path.append('./../db_scripts/')
sys.path.append('./../anomaly_scripts/')
sys.path.append('./../')
sys.path.append('./')

import argparse
import subprocess
import shlex
from scapy.all import *
from analyzer import PacketAnalyzer
import pickle

parser = argparse.ArgumentParser(description='Script to capture traffic and insert into database for training')
parser.add_argument('interface', help='Network interface to monitor')
parser.add_argument('--timeout', default=0, type=int, help='time in seconds to capture packets, default 0 for no timeout')

args = parser.parse_args()

pkt_analyzer = PacketAnalyzer(is_training_mode = False)                           
pkt_filter = ""

# Below is an example of a possible packet filter, that removes traffic for ssh (port 8001) 
# and from the monitoring machine (128.220.221.15) itself
# pkt_filter = "src port not 8001"
# pkt_filter += " and dst port not 8001"
# pkt_filter += " and ip host not 128.220.221.15"

if (args.timeout == 0): 
    sniff(iface=args.interface, store=0, prn=pkt_analyzer.process_packet, filter=pkt_filter)
else:
    sniff(iface=args.interface, store=0, prn=pkt_analyzer.process_packet, timeout = args.timeout, filter=pkt_filter)

print("Exiting\n")
