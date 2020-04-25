import argparse
from datetime import datetime
from multiprocessing import Process, Queue

from PacketAggregate import *
from predict_aggregate import MLPredictor


# Process packets and compare to 
class Processor():
    def __init__(self, baseline, models):
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
                # print(avgBucket)`

                for m in models:
                    m.predict(self.curBkt)

                self.curBkt = Bucket()
            else:
                self.firstBucket = False

        self.curBkt.update(packet)
        self.prevIndex = index


# Starts an aggregate daemon
#   baseline: The name of the baseline file (output of generate_baseline.py)
#   data: the pickled data (output of featurize_baseline.py)
#   models: list of filenames containing models  (output of train_baseline.py)
# Example usage
# aggregateDaemon(None, "baseline.out", "aggregate_features.pkl", ["aggregate_model.pkl"])
def aggregateDaemon(queue, baseline, data, models):
    baseline = pickle.load(open(baseline, 'rb')) 
    MLPredictor.loadKnown(data)

    predictors = []
    for filename in models:
        predictors.append(pickle.load(open(filename, 'rb')))

    p = Processor(baseline, models)

    while True:
        pkt = queue.get()
        p.process(pkt)
