import pickle
from multiprocessing import Queue
from __init__ import *
import psycopg2
from psycopg2.extras import DictCursor
import os, sys
import numpy as np
# import scapy
from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmptypes
from scapy.data import ETHER_TYPES

# sys.path.append('./../')

class LOFProcessor():
    def __init__(self, pkl_filename,pkl_scaler,output_file):
        self.out = open(output_file, 'w+')
        self.fields={}
        self.parsed_pkts=[]
        self.X=[]
        for index,col in enumerate(distinct_cols):
            self.fields[index]=col    
        
        print(self.fields.values(),file=self.out,flush=True)
        self.clf = pickle.load(open(pkl_filename, 'rb'))
        self.scaler = pickle.load(open(pkl_scaler, 'rb'))

       
    def process(self, parsed_pkt):
        # TODO: Maybe send transformed packets to these, as all ml models will run this function
        vec=transform(parsed_pkt, self.fields)
        nd_vals = np.asarray(list(vec.values()))#.reshape(1, -1)
        self.parsed_pkts.append(parsed_pkt)
        self.X.append(nd_vals)
        # print(nd_vals)
    
    def predict(self):
        #predictions=self.clf.predict(self.X)
        X_transformed=self.scaler.transform(self.X)
        predictions=self.clf.predict(X_transformed)
        needed=[i for i,val in enumerate(predictions) if val==-1]
        if len(needed)>=1:
            summaries=[]
            for i in needed:
                parsed_pkt=self.parsed_pkts[i]
                if Ether(parsed_pkt['raw']).haslayer(DHCP):
                    continue
                summaries.append(Ether(parsed_pkt['raw']).summary())
                #print(Ether(parsed_pkt['raw']).show())
                #print(self.X[i])
                #print(X_transformed[i])
            
            summaries=np.unique(summaries)
            d="\n"
            d.join(summaries)
            if len(summaries) >0:
                print(summaries,file=self.out,flush=True)
        

def per_pkt_daemon(queue, pkl_filename,pkl_scaler,output_file):
    '''
    conn=psycopg2.connect('dbname={} user=mini'.format("scada"))

    col_cursor = conn.cursor()
    col_query = "select column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'per_packet';"
    col_cursor.execute(col_query)
    columns=col_cursor.fetchall()
    col_cursor.close()
    fields={}
    for index,col in enumerate(columns):
        f=col[0]
        fields[index]=f
    print(fields.values())
    '''
    lof = LOFProcessor(pkl_filename,pkl_scaler,output_file)
    print("LOF Daemon called",file=lof.out,flush=True)

    while True:
        parsed_pkt =queue.get()
        if Ether(parsed_pkt['raw']).haslayer(Dot3):
            continue 
        
        if parsed_pkt.get('arp_psrc',"")=="192.168.0.120":
            continue
        if parsed_pkt.get('mac_src')=="00:e1:6d:c3:bc:06":
            continue
        """ 
        if parsed_pkt.get('arp_pdst',"")=="128.220.221.1":
            continue  
        """
        lof.process(parsed_pkt)
        if len(lof.X)>100:
            lof.predict()
            lof.X=[]
            lof.parsed_pkts=[]
