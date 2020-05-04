import pickle
import json
import sys
import numpy as np

from featurize_aggregate import featurize 

class MLPredictor():
    names = None
    known = None

    @staticmethod
    def loadKnown(data):
        (MLPredictor.known, MLPredictor.names, _) = pickle.load(open(data, 'rb'))

    def __init__(self, model):
        if (MLPredictor.known is None):
            raise Exception("MLPredictor: call loadKnown() before making and instance!")
        self.clf = pickle.load(open(model, 'rb'))
       
    def predict(self, bucket):
        if (MLPredictor.known is None):
            raise Exception("MLPredictor: call loadKnown() before prediction (needs it to featurize)")

        vec = featurize(MLPredictor.known, bucket)
        #print(json.dumps({n:v for n, v in zip(MLPredictor.names, vec)}, indent=4))

        nd_vals = np.array(vec).reshape(1, -1)
        prediction=self.clf.predict(nd_vals)
        return prediction



# test predictor on baseline buckets
if __name__ == '__main__':
    # Load known ips and feature anes
    MLPredictor.loadKnown("aggregate_features.pkl")
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
        predictor.predict(b)

