import numpy as np
import time

import argparse

import pickle
from sklearn.neighbors import LocalOutlierFactor


if  __name__=='__main__':

    # Parse command line args
    parser = argparse.ArgumentParser(description='Train models on aggregate feature data')
    parser.add_argument('--features', default='./aggregate_features.pkl', help='pickled features object')
    parser.add_argument('--model', default='./aggregate_model.pkl', help='output, pickled model')
    parser.add_argument('--algorithm', default='lof', choices=['lof'], help='algorithm to train on')

    args = parser.parse_args();

    f = open(args.features, "rb")
    (known, names, data) = pickle.load(f)

    start=time.time()
    clf=LocalOutlierFactor(n_neighbors=5,novelty=True,metric='cosine')
    clf.fit(data)

    pickle.dump(clf, open(args.model, 'wb'))
    end=time.time()
    print("Fitting done, took {:.2f}s".format(end - start))
    
    X_scores = clf.negative_outlier_factor_
    print(X_scores)
       

