import argparse
from datetime import datetime
from multiprocessing import Process, Queue

from PacketAggregate import *
from predict_aggregate import MLPredictor


# Process packets and compare to 
class AggregateProcessor():
    def __init__(self, baseline, models, data, output_file):
        
        self.out = open(output_file, 'w+')
        # for convenience
        
        # MLPredictor.loadKnown(data)
        print("Aggregate Predictor Started", flush=True, file=self.out)
        MLPredictor.loadKnown("./../ml/aggregate/aggregate_features.pkl")
        # print(baseline, flush=True, file=self.out)
        # print(models, flush=True, file=self.out)
        self.baseline = pickle.load(open(baseline, 'rb'))
        self.interval = self.baseline.interval
        self.n = self.baseline.n

        self.curBkt = Bucket()
        self.firstBucket = True
        self.prevIndex = -1

        self.predictors = []
        for filename in models:
            self.predictors.append(MLPredictor(filename))


    def printDiff(baseline, bucket):
        pass

    def process(self, packet):
        time = packet['time']
        index = int((time % self.interval) // (self.interval / self.n))
        if (self.prevIndex != -1 and index != self.prevIndex and index != (self.prevIndex + 1) % self.n):
            print("out of order packet")
            return

        if (index != self.prevIndex and self.prevIndex != -1):
            if (not self.firstBucket):
                # Predict using ml algorithms and show the diff if the majority predict abnormal
                
                num_abnormal = 0
                for p in self.predictors:
                    if (p.predict(self.curBkt) == -1):
                        num_abnormal = 1;

                if (num_abnormal > len(self.predictors) // 2):
                    print("Last minute predicted abnormal:", flush=True, file=self.out)
                    printDiff(self.baseline, self.curBkt)

                else:
                    print("Last minute predicted normal.", flush=True, file=self.out)
                
            else:
                self.firstBucket = False
            self.curBkt = Bucket()

        self.curBkt.update(packet)
        self.prevIndex = index


# Starts an aggregate daemon
#   baseline: The name of the baseline file (output of generate_baseline.py)
#   data: the pickled data (output of featurize_baseline.py)
#   models: list of filenames containing models  (output of train_baseline.py)
# Example usage
# aggregateDaemon(None, "baseline.out", "aggregate_features.pkl", ["aggregate_model.pkl"])
def aggregateDaemon(queue, baseline, models, data, output_file):
    # baseline = pickle.load(open(baseline, 'rb')) 

    p = AggregateProcessor(baseline, models, data, output_file)

    while True:
        # print("retreiving", flush=True, file=p.out)
        pkt = queue.get()
        p.process(pkt)
