import subprocess
import shlex
import pickle
import argparse
from scapy.all import *
from analyzer import PacketTester

# Change interface with any interface from tcpdump -D, or the one where you want to monitor. Can also provide list of interfaces

parser = argparse.ArgumentParser(description='Live test of anomaly detection')
parser.add_argument('--baseline', help="Pickled baseline stats for anomaly detection", required=True)
args = parser.parse_args()

with open(args.baseline, "rb") as f:
    baseline = pickle.load(f)
    count = 0
    pkt_tester = PacketTester(baseline, run_in_bg = True)
                
    filter = "src port not 8001"
    filter += " and dst port not 8001"
    filter += " and ip host not 128.220.221.15"
    sniff(iface='eth3', store=0, prn=pkt_tester.process_packet, timeout = 7200, filter=filter)
    print("FInishing up\n")
