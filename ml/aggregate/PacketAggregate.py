import json
import pickle
import numpy
from collections import defaultdict

# define here to allow pickling
def defaultVal():
    return 0

class Bucket():
    # methods for manipulating the stats of a single period
    def __init__(self):
        self.total = 0

        # define counts that count the number of packets of certain type
        # fields corr to boolean fields in db
        self.pktCounts = {
            'has_ip'   : 0,
            'has_tcp'  : 0,
            'has_udp'  : 0,
            'has_icmp' : 0,
            'has_arp'  : 0,
            'has_ether': 0,
        }

        # define fields we want to count the number of instances of each category
        # correspond to categorical fields in db
        self.categoryCounts = {
            'ip_src' : defaultdict(defaultVal),
            'ip_dst' : defaultdict(defaultVal),
            'udp_src_port' : defaultdict(defaultVal),
            'udp_dst_port' : defaultdict(defaultVal),
            'udp_len' : defaultdict(defaultVal),
            'mac_src' : defaultdict(defaultVal),
            'mac_dst' : defaultdict(defaultVal),
        }

        self.flows = {
            ('ip_src', 'ip_dst') : defaultdict(defaultVal),
            ('mac_src', 'mac_dst') : defaultdict(defaultVal),
        }

    def isZero(self):
        return self.total == 0

    # Add one packet to stats
    def update(self, packet):
        self.total += 1
        
        for field in self.pktCounts:
            if (field in packet) and packet[field]:
                self.pktCounts[field] += 1 

        for field, d in self.categoryCounts.items():
            if (field not in packet):
                d[None] += 1
            else:
                label = packet[field]
                d[label] += 1

        for (f1, f2), d in self.flows.items():
            if (f1 not in packet or f2 not in packet): continue
            d[(packet[f1], packet[f2])] += 1

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        ret = "Total packets: %d" % self.total + "\n"
        ret += "ip_src: " +  json.dumps(self.categoryCounts['ip_src'], indent = 4) + "\n"
        ret += "ip_dst: " + json.dumps(self.categoryCounts['ip_dst'], indent = 4) + "\n"
        ret += json.dumps(self.pktCounts, indent = 4) + "\n"
        ret += str(self.flows) + "\n";
        return ret

# aggregate stats
# m intervals of n buckets each
class PacketAggregate():
    def __init__(self, interval, m, n):
        self.buckets = [[Bucket() for i in range(n)] for i in range(m)]
        self.interval = interval
        self.m = m
        self.n = n

    def update(self, packet, index):
        self.buckets[index // self.n][index % self.n].update(packet)

    def print(self):
        i = 0
        for bs in self.buckets: 
            print("================= INTERVAL {} =====================".format(i))
            j = 0
            for b in bs:
                # if (b.isZero()): continue
                print("------ Bucket {} ------".format(j))
                print(b)
                j += 1
            i += 1

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
