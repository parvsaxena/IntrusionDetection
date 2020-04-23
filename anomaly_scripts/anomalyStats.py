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

    def isZero(self):
        return self.total == 0

    # Add one packet to stats
    def update(self, packet):
        self.total += 1
        
        for field in self.pktCounts:
            if (field in packet) and packet[field]:
                self.pktCounts[field] += 1 


        for field in self.categoryCounts:
            if (field not in packet): continue
            label = packet[field]
            self.categoryCounts[field][label] += 1


    # mutliply each element by c
    def scale(self, c):
        self.total *= c

        for field in self.pktCounts:
            self.pktCounts[field] *= c

        for field in self.categoryCounts:
            for label in self.categoryCounts[field]:
                self.categoryCounts[field][label] *= c

    # Get the difference of stats (other is baseline)
    def diff(self, other):
        ret = Bucket();
        ret.total = self.total - other.total
        for field in self.pktCounts:
            ret.pktCounts[field] = self.pktCounts[field] - other.pktCounts[field]

        for field in self.categoryCounts:
            a = self.categoryCounts[field]
            b = other.categoryCounts[field]
            a_keys = set(a.keys())
            b_keys = set(b.keys())

            # any values that didn't appear are marked as 'other'
            for l in b_keys.difference(a_keys):
                ret.categoryCounts[field]['other'] += a[l]

            # for all keys in baseline, find difference
            for l in a_keys:
                ret.categoryCounts[field][l] = a[l] - b[l];

        return ret

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        ret = "Total packets: %d" % self.total + "\n"
        ret +=  json.dumps(self.categoryCounts, indent = 4) + "\n"
        ret += json.dumps(self.pktCounts, indent = 4) + "\n"
        return ret

# aggregate stats
# m intervals of n buckets each
class AnomalyStats():
    def __init__(self, interval, m, n):
        self.buckets = [[Bucket() for i in range(n)] for i in range(m)]
        self.interval = interval
        self.m = m
        self.n = n

    def update(self, packet, index):
        self.buckets[index // self.n][index % self.n].update(packet)

    # average the values along over bucket index  and return new bucket
    def avg(self, bktIndex):
        num = 0
        ret = Bucket()
        for interval in self.buckets:
            bkt = interval[bktIndex]

            # First or last bucket, partial data we don't want to include
            if (bktIndex > 0 and interval[bktIndex - 1].isZero()): continue
            if (bktIndex < self.n - 1 and interval[bktIndex + 1].isZero()): continue
            if (bkt.isZero()): continue

            ret.total += bkt.total
            for field in bkt.pktCounts:
                ret.pktCounts[field] += bkt.pktCounts[field]

            for field in bkt.categoryCounts:
                for label in bkt.categoryCounts[field]:
                    ret.categoryCounts[field][label] += bkt.categoryCounts[field][label]
            num += 1

        ret.scale(1/num);
        return ret

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
