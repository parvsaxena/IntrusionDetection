import json
import pickle
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
        }

        # define fields we want to count the number of instances of each category
        # correspond to categorical fields in db
        self.categoryCounts = {
            'ip_src' : defaultdict(defaultVal),
            'ip_dst' : defaultdict(defaultVal),
            'udp_dst_port' : defaultdict(defaultVal),
            'udp_dst_port' : defaultdict(defaultVal),
            'udp_len' : defaultdict(defaultVal),
        }

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


    def __str__(self):
        ret = "Total packets: %d" % self.total + "\n"
        ret +=  json.dumps(self.categoryCounts, indent = 4) + "\n"
        ret += json.dumps(self.pktCounts, indent = 4) + "\n"
        return ret

# aggregate stats
class AnomalyStats():
    def __init__(self, interval, n):
        self.buckets = [Bucket() for i in range(n)]
        self.interval = interval
        self.n = n 
        # number of times a bucket has been added to (to compute avg) 
        self.numData = [0 for i in range(n)]

    # add to stats
    def addToAvg(self, index, bkt):
        AnomalyStats.avg(self.buckets[index], bkt, self.numData[index])
        self.numData[index] += 1

    @staticmethod
    # add the values in bucket to the averages in avgbucket
    def avg(avgBucket, bucket, n):
        avgBucket.total = (avgBucket.total * n + bucket.total) / (n + 1)

        for field in avgBucket.pktCounts:
            curVal = avgBucket.pktCounts[field]
            avgBucket.pktCounts[field] = (curVal * n + bucket.pktCounts[field]) / (n + 1)

        for field in avgBucket.categoryCounts:
            for label in bucket.categoryCounts[field]:
                curVal = avgBucket.categoryCounts[field][label]
                avgBucket.categoryCounts[field][label] = (curVal * n + bucket.categoryCounts[field][label]) / (n + 1)

    def print(self):
        for b in self.buckets: print(b)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
