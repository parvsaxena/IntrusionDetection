import sys
sys.path.append('./../db_scripts/')
sys.path.append('./../anomaly_scripts/')
sys.path.append('./../')


import subprocess
import shlex
from scapy.all import *
from analyzer import PacketAnalyzer
import pickle

# Change interface with any interface from tcpdump -D, or the one where you want to monitor. Can also provide list of interfaces
count = 0

baseline = None
# with open("./../baseline.out", "rb") as f:
#     baseline = pickle.load(f)


pkt_analyzer = PacketAnalyzer(run_in_bg = True,
                              is_training_mode = True,
                              disable_db_insertion = False,
                              baseline = baseline)


filter = "src port not 8001"
filter += " and dst port not 8001"
filter += " and ip host not 128.220.221.15"
sniff(iface='eth3', store=0, prn=pkt_analyzer.process_packet, timeout = 3600*6, filter=filter)
print("FInishing up\n")

# for pkt in sniff(iface='wlp58s0', store=0, prn=parse_packet):
    # count = count + 1
    # print("Packet no", count)
    # print("Packet ether qualtities are", pkt.src, pkt.dst)
    # parse_packet(pkt)


