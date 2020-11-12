import sys
sys.path.append('./../db_scripts/')
sys.path.append('./../anomaly_scripts/')
sys.path.append('./../')
sys.path.append('./')

import argparse
import subprocess
import scapy
from scapy.all import sniff
from analyzer import PacketAnalyzer
import pickle

parser = argparse.ArgumentParser(description='Script to capture traffic and insert into database for training')
parser.add_argument('interface', help='Network interface to monitor')
parser.add_argument('--timeout', default=3600, type=int, help='time in seconds to capture packets, default 3600 sec or 1 hr')

args = parser.parse_args()

pkt_analyzer = PacketAnalyzer(is_training_mode = True)
pkt_filter = ""

# Below is an example of a possible packet filter, that removes traffic for ssh (port 8001) 
# and from the monitoring machine (128.220.221.15) itself
# pkt_filter = "src port not 8001"
# pkt_filter += " and dst port not 8001"
# pkt_filter += " and ip host not 128.220.221.15"


sniff(iface=args.interface, store=0, prn=pkt_analyzer.process_packet, timeout = args.timeout, filter=pkt_filter)

print("Exiting\n")



