import argparse
import numpy as np

from datetime import datetime
from multiprocessing import Process, Queue

from PacketAggregate import *
from predict_aggregate import MLPredictor
from featurize_aggregate import featurize

# Process packets and compare to 
class AggregateProcessor():

    # Given the filenames of data/output log, creates processor
    #   baseline    - output of generate_aggregate.py 
    #   models      - output of train_aggregate.py
    #   data        - output of featurize_aggregate.py
    #   output_file - file that this prints to
    def __init__(self, baseline, models, data, output_file):
        self.out = open(output_file, 'w+')
        
        print("Aggregate Predictor Started", flush=True, file=self.out)

        # Load training data so we can make comparisons
        (self.known, self.names, data) = pickle.load(open(data, 'rb'))

        self.avg = np.average(data, axis = 0)
        self.std = np.std(data, axis = 0)

        # Load baseline because we need to know bucket size 
        baseline = pickle.load(open(baseline, 'rb'))
        self.interval = baseline.interval
        self.n = baseline.n

        # Initialize current bucket and variables to keep track of it
        self.curBkt = Bucket()
        self.firstBucket = True
        self.prevIndex = -1

        self.predictors = []
        for filename in models:
            self.predictors.append(MLPredictor(filename))


    def printDiff(self, vec):

        for (field, val, mu, sigma) in zip(self.names, vec, self.avg, self.std):
            # don't print out fields that have small differences
            if (sigma == 0):
                if (abs(val - mu) <= 1):
                    continue
            elif (abs((val - mu) / sigma) <= 2.0):
                continue

            template = "  {0:30} - cur {1:5d}, avg {2:5.0f} ({3:+.0f})"
            template = template.format(field, val, mu, val - mu)
            if (sigma != 0):
                template += " ({0:+.2f} stds)"
                template = template.format((val - mu) / sigma)

            print(template, flush=True, file=self.out)
        

    def process(self, packet):
        time = packet['time']
        index = int((time % self.interval) // (self.interval / self.n))
        if (self.prevIndex != -1 and index != self.prevIndex and index != (self.prevIndex + 1) % self.n):
            print("out of order packet")
            return

        if (index != self.prevIndex and self.prevIndex != -1):
            if (not self.firstBucket):
                # Predict using ml algorithms and show the diff if the majority predict abnormal
                features = featurize(self.known, self.curBkt)

                num_abnormal = 0
                for p in self.predictors:
                    if (p.predict(features) == -1):
                        num_abnormal = 1;

                if (num_abnormal > len(self.predictors) // 2):
                    print("Last minute predicted abnormal:", flush=True, file=self.out)
                    self.printDiff(features)

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
