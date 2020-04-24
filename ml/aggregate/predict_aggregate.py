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
        self.data = data
       
    def process(self, bucket):
        vec = featurize(self.known, bucket)
        #print(vec)
        #print(self.data[0])

        nd_vals = np.array(vec).reshape(1, -1)
        prediction=self.clf.predict(nd_vals)

        print("Prediction=",prediction[0])


if __name__ == '__main__':
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


    for b in bkts:
        processor.process(b)
