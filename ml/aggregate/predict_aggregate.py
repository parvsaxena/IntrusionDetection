import pickle
import json
import sys
import numpy as np

from featurize_aggregate import featurize 

class MLPredictor():
    names = None
    known = None

    def __init__(self, model):
        (self.use_flows, self.scaler, self.pca, self.clf) = pickle.load(open(model, 'rb'))
        self.model = model
       
    def predict(self, vec):
        # note this is hard coded for 18 flow features at end!!!!!!
        if (self.use_flows): vec = vec[:-18]
        
        vec = np.array(vec).reshape(1, -1)
        
        if (self.scaler is not None):
            vec = self.scaler.transform(vec)

        if (self.pca is not None):
            vec = self.pca.transform(vec)

        prediction = self.clf.predict(vec)
        return prediction



# test predictor on baseline buckets
if __name__ == '__main__':
    # Load known ips and feature anes
    (known, names, data) = pickle.load(open("aggregate_features.pkl", 'rb'))
    predictor = MLPredictor("lof_pca20.pkl")

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
        vec = featurize(known, b)
        print(predictor.predict(vec))


