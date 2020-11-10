import pickle
import numpy as np


class MLPredictor():
    def __init__(self, clf, name, use_flows, scaler, pca):
        self.clf = clf
        self.name = name
        self.use_flows = use_flows
        self.scaler = scaler 
        self.pca = pca 
       
    def predict(self, vec, flow_vec):
        if (self.use_flows): vec += flow_vec
        
        vec = np.array(vec).reshape(1, -1)
        
        if (self.scaler is not None):
            vec = self.scaler.transform(vec)

        if (self.pca is not None):
            vec = self.pca.transform(vec)

        prediction = self.clf.predict(vec)
        return prediction


