import pickle
import json
import sys
import numpy as np

from featurize_aggregate import featurize 

class MLPredictor():
    names = None
    known = None

    def __init__(self, model):
        self.clf = pickle.load(open(model, 'rb'))
       
    def predict(self, vec):
        nd_vals = np.array(vec).reshape(1, -1)
        prediction = self.clf.predict(nd_vals)
        return prediction



# test predictor on baseline buckets
if __name__ == '__main__':
    # Load known ips and feature anes
    (known, names, _) = pickle.load(open("aggregate_features.pkl", 'rb'))
    predictor = MLPredictor("aggregate_model.pkl")

    f = open("./baseline.out", "rb")
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
        print(predictor.predict(featurize(known, b)))


