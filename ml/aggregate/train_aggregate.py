import numpy as np
import time

import argparse

import pickle
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import train_test_split
from sklearn import svm


if __name__ != '__main__':
    print('featurize_aggregate.py: should be run as a script')
    exit(1)

# Parse command line args
parser = argparse.ArgumentParser(description='Train models on aggregate feature data')
parser.add_argument('--features', default='./aggregate_features.pkl', help='pickled features object')
parser.add_argument('--model', default='./aggregate_model.pkl', help='output, pickled model')
parser.add_argument('--algorithm', default='lof', choices=['lof', 'svm'], help='algorithm to train on')
parser.add_argument('--use_flows', help='whether to use the flow related features in the data')

args = parser.parse_args();

f = open(args.features, "rb")
(known, names, data) = pickle.load(f)

# TODO Note this is hard coded to remove last 18 features because there are 18 features in featurize_aggregate.py
if (args.use_flows is None):
    data = data[:, :-18]


start = time.time()


# Split data
train, test = train_test_split(data, test_size=0.2)

if (args.algorithm == 'lof'):
    clf=LocalOutlierFactor(n_neighbors=30,novelty=True)
    clf.fit(train)
    X_scores = clf.negative_outlier_factor_
    print(X_scores)
elif (args.algorithm == 'svm'):
    clf = svm.OneClassSVM()
    clf.fit(train)


results = clf.predict(test)
num_correct = np.count_nonzero(results + 1)
print('{}/{} of test data correct {:.2f}'.format(
    num_correct, 
    len(results), 
    num_correct/len(results)
))

pickle.dump((args.use_flows is None, clf), open(args.model, 'wb'))
end=time.time()
print("Fitting done, took {:.2f}s".format(end - start))

   

