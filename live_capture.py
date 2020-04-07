import subprocess
import shlex
from scapy.all import *
from analyzer import PacketAnalyzer


# Change interface with any interface from tcpdump -D, or the one where you want to monitor. Can also provide list of interfaces
count = 0
pkt_analyzer = PacketAnalyzer(run_in_bg = True) 
sniff(iface='eth3', store=0, prn=pkt_analyzer.parse_packet, timeout = 600)
print("FInishing up\n")
# for pkt in sniff(iface='wlp58s0', store=0, prn=parse_packet):
    # count = count + 1
    # print("Packet no", count)
    # print("Packet ether qualtities are", pkt.src, pkt.dst)
    # parse_packet(pkt)


# output = subprocess.check_output(shlex.split("""tshark -l"""))
# process = subprocess.Popen(shlex.split("""sudo tcpdump --immediate-mode -U -w -"""), stdout=subprocess.PIPE, stderr=None)
# print(process.stdout.readline())
#
# for pkt_data, pkt_metadata in RawPcapReader(process.stdout):
#     print(pkt_data)
# for line in iter(process.stdout.readline, b''):
#     pkt_data, pkt_metadata = RawPcapReader(line)
#     print(pkt_data)
