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

pkt_analyzer = PacketAnalyzer(is_training_mode = True)


# Currently filtering/avoiding traffic to/from mini1, and that of ssh(port 8001)
#Tiomeout is is set in sec to capture training traffic for that duration
filter = "src port not 8001"
filter += " and dst port not 8001"
filter += " and ip host not 128.220.221.15"
sniff(iface='eth3', store=0, prn=pkt_analyzer.process_packet, timeout = 3600*6, filter=filter)
print("FInishing up\n")



