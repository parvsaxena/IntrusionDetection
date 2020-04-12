import json
from collections import defaultdict

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
            'ip_src' : defaultdict(lambda: 0),
            'ip_dst' : defaultdict(lambda: 0),
        }

    # Add one packet to stats
    def update(self, packet):
        self.total += 1
        
        for field in self.pktCounts:
            if (packet[field]):
                self.pktCounts[field] += 1 


        for field in self.categoryCounts:
            label = packet[field]
            if (label == None): continue
            self.categoryCounts[field][label] += 1

    
    def __str__(self):
        ret = "Total packets: %d" % self.total + "\n" + json.dumps(self.categoryCounts) + "\n"
        ret += json.dumps(self.pktCounts) + "\n"
        return ret

# aggregate stats
class AnomalyStats():
    def __init__(self, n):
        self.buckets = [Bucket() for i in range(n)]
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
