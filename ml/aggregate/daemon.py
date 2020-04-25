import argparse
from datetime import datetime
from multiprocessing import Process, Queue

from PacketAggregate import *


# Process packets and compare to 
class Processor():
    def __init__(self, baseline):
        # for convenience
        self.baseline = baseline
        self.interval = baseline.interval
        self.n = baseline.n

        self.curBkt = Bucket()
        self.firstBucket = True
        self.prevIndex = -1

    def process(self, packet):
        time = packet['time']
        index = int((time % self.interval) // (self.interval / self.n))
        if (self.prevIndex != -1 and index != self.prevIndex and index != (self.prevIndex + 1) % self.n):
            print("out of order packet")
            return

        if (index != self.prevIndex and self.prevIndex != -1):
            if (not self.firstBucket):
                # print the differnce between baseline and current stats
                # TODO something here
                avgBucket = self.baseline.avg(index)
                print("Bucket Num=",index)
                print(self.curBkt.diff(avgBucket))
                # print(self.cur)
                # print(avgBucket)
                self.curBkt = Bucket()
            else:
                self.firstBucket = False

        self.curBkt.update(packet)
        self.prevIndex = index


def AggregateDaemon(queue, baseline):
    p = Processor(baseline)

    while True:
        pkt = queue.get()
        p.process(pkt)
