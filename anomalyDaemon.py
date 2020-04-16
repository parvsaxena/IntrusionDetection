import argparse
from datetime import datetime
from multiprocessing import Process, Queue

from anomalyStats import *


# Process packets and compare to 
class PacketProcessor():
    def __init__(self, baseline):
        # for convenience
        self.interval = baseline.interval
        self.n = baseline.n
        self.baseline = baseline

        self.cur = Bucket()
        self.firstBucket = True
        self.prevIndex = self.n

    def process(self, packet):
        time = packet['time']
        index = int((time % (60 * self.interval)) // (60 * self.interval / self.n))
        
        if (index != self.prevIndex and self.prevIndex != self.n):
            if (self.firstBucket):
                self.firstBucket = False
                return
            # print the differnce between baseline and current stats
            print(self.cur.diff(self.baseline.buckets[self.prevIndex]))
            print(self.cur)
            print(self.baseline.buckets[self.prevIndex])
            self.cur = Bucket()

        self.cur.update(packet)
        self.prevIndex = index
    


def AnomalyDaemon(queue, baseline):
    p = PacketProcessor(baseline)

    while True:
        pkt = queue.get()
        p.process(pkt)
