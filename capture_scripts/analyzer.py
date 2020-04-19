import sys
sys.path.append('./../db_scripts/')
sys.path.append('./../anomaly_scripts/')
sys.path.append('./../')

from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES
from multiprocessing import Process, Queue
from dbDaemon import dbDriver, dbDaemon
from anomalyDaemon import PacketProcessor, AnomalyDaemon
import argparse
import pickle
import os


# Time ??, Source IP(d), Destination IP(d), Protocol ??, Length(d),
# Source Port(d), Dest Port(d), TTL(d), IP version ??
# https://www.howtoinstall.co/en/ubuntu/xenial/tshark      

db_name = "scada"
def expand(x):
    yield x.name
    while x.payload:
        x = x.payload
        yield x.name

def extract_ip(parsed_dict, ip_pkt):
    parsed_dict['ip_src'] = ip_pkt.src
    parsed_dict['ip_dst'] = ip_pkt.dst
    parsed_dict['ip_ttl'] = ip_pkt.ttl
    parsed_dict['ip_len'] = ip_pkt.len
    parsed_dict['ip_ver'] = ip_pkt.version
    # TODO: prototype number to name translation
    parsed_dict['proto'] = ip_pkt.proto
    parsed_dict['has_ip'] = True

def extract_ether(parsed_dict, ether_pkt):
    parsed_dict['mac_src'] = ether_pkt.src
    parsed_dict['mac_dst'] = ether_pkt.dst
    parsed_dict['ether_type'] = ether_pkt.type
    parsed_dict['has_ether'] = True
    # https://github.com/secdev/scapy/blob/master/scapy/libs/ethertypes.py
    # print(ETHER_TYPES['IPV4'])

def extract_tcp(parsed_dict, tcp_pkt):
    parsed_dict['tcp_src_port'] = tcp_pkt.sport
    parsed_dict['tcp_dst_port'] = tcp_pkt.dport
    parsed_dict['has_tcp'] = True

def extract_udp(parsed_dict, udp_pkt):
    parsed_dict['udp_src_port'] = udp_pkt.sport
    parsed_dict['udp_dst_port'] = udp_pkt.dport
    parsed_dict['udp_len'] = udp_pkt.len
    parsed_dict['has_udp'] = True

def extract_icmp(parsed_dict, icmp_pkt):
    #print(icmp_pkt.summary())
    # TODO: Ask which more fields are necessary
    parsed_dict['icmp_type'] = icmp_pkt.type  # 0 for request, 8 for reply
    #parsed_dict['icmp_type_str'] = icmptypes[icmp_pkt.type]
    parsed_dict['icmp_code'] = icmp_pkt.code  # code field which gives extra information about icmp type
    parsed_dict['has_icmp'] = True

def extract_arp(parsed_dict, arp_pkt):
    #print(arp_pkt.summary())
    parsed_dict['arp_op'] = arp_pkt.op # 1 who-has, 2 is-at
    parsed_dict['arp_psrc'] = arp_pkt.psrc
    parsed_dict['arp_pdst'] = arp_pkt.pdst
    parsed_dict['arp_hwsrc'] = arp_pkt.hwsrc
    parsed_dict['arp_hwdst'] = arp_pkt.hwdst
    parsed_dict['has_arp'] = True

def isAttackPacket(parsed_dict):
    # TODO: Add logic for identifying attack packets during data generation here
    parsed_dict['is_attack_pkt'] = False

# raw packet to parsed dictionary
def parse_packet(pkt_data):
    # TODO: Initialize data
    parsed_dict = {}
    #Parse arrival time
    parsed_dict['time'] = pkt_data.time

    # print(tape(ip_pkt))
    if pkt_data.haslayer(Ether):
        #print("Ether layer exists")
        ether_pkt = pkt_data.getlayer(Ether)
        extract_ether(parsed_dict, ether_pkt)
    # TODO: Extract ports
    # TODO: Do we need IPv6 support?
    # IP packet
    if pkt_data.haslayer(IP):
        #print("Received IP packet")
        ip_pkt = pkt_data.getlayer(IP)
        extract_ip(parsed_dict, ip_pkt)
        # print(ip_pkt.show())
 
    if pkt_data.haslayer(TCP):
        #print("TCP layer exists")
        tcp_pkt = pkt_data.getlayer(TCP)
        extract_tcp(parsed_dict, tcp_pkt)

    if pkt_data.haslayer(UDP):
        udp_pkt = pkt_data.getlayer(UDP)
        extract_udp(parsed_dict, udp_pkt)

        #print("UDP layer exists")
    if pkt_data.haslayer(ARP):
        #print("ARP layer exists")
        arp_pkt = pkt_data.getlayer(ARP)
        extract_arp(parsed_dict, arp_pkt)
    if pkt_data.haslayer(ICMP):
        icmp_pkt = pkt_data.getlayer(ICMP)
        extract_icmp(parsed_dict, icmp_pkt)
    return parsed_dict


class PacketAnalyzer:
    def __init__(self, run_in_bg, is_training_mode, disable_db_insertion, baseline):
        if run_in_bg == True:
            # requires setting up queue, and starting zombie process
            # TODO: optimize and dont create some queues in trainig.testing mode
            # Db insertion queue
            self.pqueue = Queue()
            db_insertion_process = Process(target=dbDaemon, args=(self.pqueue,))
            print("Creating",  db_insertion_process.name, db_insertion_process.pid)
            db_insertion_process.daemon = True
            db_insertion_process.start()
            
            if is_training_mode == False:
                # ML prediction queue
                self.ml_queue = Queue()
                prediction_process = Process(target=AnomalyDaemon, args=(self.ml_queue,baseline))
                print("Creating", prediction_process.name, prediction_process.pid)
                prediction_process.daemon = True
                prediction_process.start()
            else:
                self.ml_queue = None
                # self.pkt_p = PacketProcessor(baseline)

        else:
            self.pqueue = None
            self.db = dbDriver(db_name)
            
            if is_training_mode == False:
                self.ml_queue = None
                self.pkt_p = PacketProcessor(baseline)
            else:
                self.ml_queue = None

        self.packet_count = 0
        self.is_training_mode = is_training_mode
        self.disable_db_insertion = disable_db_insertion
    
    def process_packet(self, pkt_data):
        parsed_dict = parse_packet(pkt_data)
        self.packet_count = self.packet_count + 1

        # if self.packet_count % 100 == 0:
        #     print ("******packet_count={}".format(self.packet_count))
        
        # Adding Raw dump
        raw_dump = raw(pkt_data)
        parsed_dict['raw'] = raw_dump
        # Adding training/testing flag
        parsed_dict['is_training'] = self.is_training_mode
        
        self.insert_packet(parsed_dict)
        # If testing mode, call predict_packet
        if self.is_training_mode == False:
            self.predict_packet(parsed_dict)
 
    def insert_packet(self, parsed_dict):
        if self.disable_db_insertion == True:
            return
        
        if self.pqueue is None:
            print("fg insertion")
            raw_dump = parsed_dict.pop('raw')
            self.db.insert_packet(raw_dump, parsed_dict)
        else:
            # print("bg insertion")
            # print("raw is", parsed_dict['raw'])
            self.pqueue.put(parsed_dict)
            # print("Queue size", self.pqueue.qsize())
            if self.pqueue.qsize() > 1000:
                print ("DB instertion Queue is too high")
                print("Queue size", self.pqueue.qsize())
                # exit(-1)

    def predict_packet(self, parsed_dict):
        # parsed_dict = parse_packet(pkt_data)
        
        # TODO: Remove raw and is_training
        # parsed_dict.pop('raw')
        # parsed_dict.pop('is_training')


        if self.ml_queue is None:
            print("fg prediction")
            self.pkt_p.process(parsed_dict)
        else:
            # print("bg prediction")
            self.ml_queue.put(parsed_dict)
            if self.ml_queue.qsize() > 100:
                print ("Prediction Queue is too high")
                print("Queue size", self.ml_queue.qsize())
                # exit(1)


# Passes packets to anomaly detector
class PacketTester:
    def __init__(self, baseline, run_in_bg):
        if run_in_bg == True:
            # requires setting up queue, and starting zombie process
            self.pqueue = Queue()
            testing_process = Process(target=AnomalyDaemon, args=(self.pqueue,baseline))
            print("Creating", testing_process.name, testing_process.pid)
            testing_process.daemon = True
            testing_process.start()


        else:
            self.pqueue = None
            self.p = PacketProcessor(baseline)
        self.packet_count = 0


count = 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pcap analyzer')
    parser.add_argument('--pcap', help="provide pcap to analyze", required=True)
    parser.add_argument('--mode', choices=['test', 'train'], help="Run pipeline in training/testing mode", required=True)
    parser.add_argument('--baseline', help="Pickled baseline stats for anomaly detection")
    parser.add_argument('--disable_db_insert', choices=["yes"], help="disable insertion into db")
    
    parser.add_argument('--run_in_bg', choices=["no"], help="whether to spawn daemons to run in bg")       
    args = parser.parse_args()
    
    disable_db_insertion = False
    if args.disable_db_insert:
        print("argument passed to disable db insertion")
        disable_db_insertion = True
    
    run_in_bg = True
    if args.run_in_bg:
        print("arg passed to not run in background")       
        run_in_bg = True
    
    exit(0)
    if (args.mode == "train"):
        # Pass correct args
        pkt_analyzer = PacketAnalyzer(run_in_bg = run_in_bg,
                                      is_training_mode = True, 
                                      disable_db_insertion = disable_db_insertion, 
                                      baseline = None)
        for pkt_data, pkt_metadata in RawPcapReader(args.pcap):
            packet = pkt_analyzer.process_packet(Ether(pkt_data))
    
    elif (args.mode == "test"):
        if (not args.baseline):
            print("mode needs arg --baseline!")
            exit(1)
        
        with open(args.baseline, "rb") as f: 
            baseline = pickle.load(f)
            pkt_tester = PacketAnalyzer(run_in_bg = run_in_bg,
                                        is_training_mode = False, 
                                        disable_db_insertion = disable_db_insertion, 
                                        baseline = None)
            
            for pkt_data, pkt_metadata in RawPcapReader(args.pcap):
                packet = pkt_tester.process_packet(Ether(pkt_data))
    else:
        print("invalid mode!")
        

