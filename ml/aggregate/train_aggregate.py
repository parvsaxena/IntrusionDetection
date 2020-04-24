import numpy as np
import time

import argparse

import pickle
from sklearn.neighbors import LocalOutlierFactor
from sklearn import svm


if __name__ != '__main__':
    print('featurize_aggregate.py: should be run as a script')
    exit(1)

# Parse command line args
parser = argparse.ArgumentParser(description='Train models on aggregate feature data')
parser.add_argument('--features', default='./aggregate_features.pkl', help='pickled features object')
parser.add_argument('--model', default='./aggregate_model.pkl', help='output, pickled model')
parser.add_argument('--algorithm', default='lof', choices=['lof', 'svm'], help='algorithm to train on')

args = parser.parse_args();

f = open(args.features, "rb")
(known, names, data) = pickle.load(f)

start=time.time()

if (args.algorithm == 'lof'):
    clf=LocalOutlierFactor(n_neighbors=5,novelty=True,metric='cosine')
    clf.fit(data)
    X_scores = clf.negative_outlier_factor_
    print(X_scores)
elif (args.algorithm == 'svm'):
    clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    clf.fit(data)
    print(clf.predict(data))

pickle.dump(clf, open(args.model, 'wb'))
end=time.time()
print("Fitting done, took {:.2f}s".format(end - start))

   

