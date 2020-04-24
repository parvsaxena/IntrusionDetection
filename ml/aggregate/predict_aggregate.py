import pickle
import sys
import numpy as np
sys.path.append('./../../anomaly_scripts/')

from featurize_aggregate import featurize 

class LOFAggregateProcessor():
    def __init__(self, model, data):
        self.clf = pickle.load(open(model, 'rb'))
        (known, names, data) = pickle.load(open(data, 'rb'))
        self.known = known
       
    def process(self, bucket):
        vec=featurize(self.known, bucket)
        nd_vals = np.array(vec).reshape(1, -1)
        prediction=self.clf.predict(nd_vals)

        print("Prediction=",prediction[0])


processor = LOFAggregateProcessor("aggregate_model.pkl", "aggregate_features.pkl")


f = open("../../anomaly_scripts/baseline.out", "rb")
baseline = pickle.load(f)

# Flatten buckets from baseline
bkts = []
lastBkt = None
for interval in baseline.buckets:
    for b in interval:
        if (b.isZero()):
            continue
        bkts.append(b)

# remove partial buckets
bkts.pop(len(bkts) - 1)
bkts.pop(0)


for b in bkts:
    processor.process(b)
