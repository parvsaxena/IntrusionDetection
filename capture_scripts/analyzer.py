import sys
sys.path.append('./../db_scripts/')
sys.path.append('./../anomaly_scripts/')
sys.path.append('./../')
sys.path.append('./../ml/packet')
sys.path.append('./../ml/aggregate/')

from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES
from multiprocessing import Process, Queue
from dbDaemon import dbDriver, dbDaemon
# from anomalyDaemon import PacketProcessor, AnomalyDaemon
from perPktDaemon import lorDaemon, LORProcessor
from daemon import aggregateDaemon, AggregateProcessor
from model_paths import model_paths
import argparse
import pickle
import os



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
    parsed_dict['icmp_type'] = icmp_pkt.type  # 0 for request, 8 for reply
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

# Field not really used in logic anywhere
def isAttackPacket(parsed_dict):
    parsed_dict['is_attack_pkt'] = False

# Given a raw packet, parse out features in form of a dictionary
def parse_packet(pkt_data):
    
    # TODO: Initialize data
    parsed_dict = {}
    # Parse arrival time
    parsed_dict['time'] = pkt_data.time

    if pkt_data.haslayer(Ether):
        ether_pkt = pkt_data.getlayer(Ether)
        extract_ether(parsed_dict, ether_pkt)
    
    # TODO: Do we need IPv6 support?
    # IP packet
    if pkt_data.haslayer(IP):
        ip_pkt = pkt_data.getlayer(IP)
        extract_ip(parsed_dict, ip_pkt)
 
    if pkt_data.haslayer(TCP):
        tcp_pkt = pkt_data.getlayer(TCP)
        extract_tcp(parsed_dict, tcp_pkt)

    if pkt_data.haslayer(UDP):
        udp_pkt = pkt_data.getlayer(UDP)
        extract_udp(parsed_dict, udp_pkt)

    if pkt_data.haslayer(ARP):
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
            
            # Db insertion queue
            self.pqueue = Queue()
            db_insertion_process = Process(target=dbDaemon, 
                                           args=(self.pqueue,))
            print("Creating",  db_insertion_process.name, db_insertion_process.pid)
            db_insertion_process.daemon = True
            db_insertion_process.start()
            
            if is_training_mode == False:
                # List of ML prediction queues
                self.ml_queue = []
                
                # Aggregate based daemon
                self.ml_queue.append(Queue())
                prediction_process = Process(target=aggregateDaemon, 
                                             args=(self.ml_queue[0],
                                                   model_paths["Agg_Baseline"],
                                                   model_paths["Agg_Model"], 
                                                   model_paths["Agg_Featurized_Baseline"],
                                                   model_paths["Agg_output"]))
                
                prediction_process.daemon = True
                prediction_process.start()
                
                #LOR
                self.ml_queue.append(Queue())
                prediction_process2 = Process(target=lorDaemon,
                                              args=(self.ml_queue[1], 
                                                    model_paths["LORProcessor"],
                                                    model_paths["scaler"],
                                                    model_paths["perPkt_output"]))
                
                # print("Creating lor ", prediction_process2.name, prediction_process2.pid)
                prediction_process2.daemon = True
                prediction_process2.start()
                
            else:
                self.ml_queue = None
                # self.pkt_p = None
                # self.pkt_p = PacketProcessor(baseline)

        else:
            self.pqueue = None
            self.db = dbDriver(db_name)
            
            if is_training_mode == False:
                self.ml_queue = None
                self.pkt_p = []
                
                # Aggregate Processor
                self.pkt_p.append(AggregateProcessor(model_paths["Agg_Baseline"],
                                                     model_paths["Agg_Model"],
                                                     model_paths["Agg_Featurized_Baseline"],
                                                     model_paths["Agg_output"]))
                
                # PerPacketProcessor
                """
                self.pkt_p.append(LORProcessor(model_paths["LORProcessor"],
                                               model_paths["scaler"],
                                               model_paths["perPkt_output"]))
                """
            
            else:
                self.ml_queue = None
                self.pkt_p = None

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
        
        # Insert into db
        self.insert_packet(parsed_dict)
        
        # If testing mode, call predict_packet
        if self.is_training_mode == False:
            self.predict_packet(parsed_dict)
    
    # Db insertion queue/class
    def insert_packet(self, parsed_dict):
        if self.disable_db_insertion == True:
            return
        
        if self.pqueue is None:
            # print("fg insertion")
            raw_dump = parsed_dict.pop('raw')
            self.db.insert_packet(raw_dump, parsed_dict)
        else:
            # print("bg insertion")
            self.pqueue.put(parsed_dict)
            if self.pqueue.qsize() > 1000:
                print ("DB instertion Queue is too high")
                print("Queue size", self.pqueue.qsize())
                # exit(-1)
    
    # Prediction/Anomaly queue/class
    def predict_packet(self, parsed_dict):
        if self.ml_queue is None:
            # print("fg prediction")
            for model in self.pkt_p:
                model.process(parsed_dict)
        else:
            for queue in self.ml_queue:
                # print("bg prediction")
                queue.put(parsed_dict)
                if queue.qsize() > 100:
                    print ("Prediction Queue is too high")
                    print("Queue size", queue.qsize())
                    # exit(-1)


count = 0

# Use main, if you want to read data from pcap, instead of capturing it via live traffic
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
        

