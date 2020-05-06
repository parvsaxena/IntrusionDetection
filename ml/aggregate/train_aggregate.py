import numpy as np
import time

import argparse

import pickle
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.covariance import EllipticEnvelope


if __name__ != '__main__':
    print('featurize_aggregate.py: should be run as a script')
    exit(1)

# Parse command line args
parser = argparse.ArgumentParser(description='Train models on aggregate feature data')
parser.add_argument('--features', default='./aggregate_features.pkl', help='pickled features object')
parser.add_argument('--model', default='./aggregate_model.pkl', help='output, pickled model')
parser.add_argument('--algorithm', default='lof', choices=['lof', 'svm', 'cov'], help='algorithm to train on')
parser.add_argument('--use_flows', action='store_true', help='whether to use the flow related features in the data')
parser.add_argument('--no_standardize', action='store_false', help='whether to use the flow related features in the data')
parser.add_argument('--pca', default='0', type=int, help='number of components to run PCA on')
parser.add_argument('--test_split', default='0', type=float, help='percentage of data to test on')

args = parser.parse_args();

f = open(args.features, "rb")
(known, names, data) = pickle.load(f)

# TODO Note this is hard coded to remove last 18 features because there are 18 features in featurize_aggregate.py
if (not args.use_flows):
    print("removing flow features")
    data = data[:, :-18]


start = time.time()

# Standardize data (becomes mean 0 variance 1 for each feature)
scaler = None
if (args.no_standardize):
    print("Standardizing data")
    scaler = StandardScaler().fit(data)
    data = scaler.transform(data)

# Optionally use PCA to reduce dimensions of feature space
pca = None
if (args.pca > 0):
    print("Applying PCA: Reduce {} dims to {} components".format(data.shape[1], args.pca))
    pca = PCA(n_components=args.pca)
    data = pca.fit_transform(data)
    

# Split data
if (args.test_split == 0):
    train, test = data, None
else:
    train, test = train_test_split(data, test_size=args.test_split)

# Fit classifier
if (args.algorithm == 'lof'):
    clf = LocalOutlierFactor(n_neighbors=30,novelty=True)
    clf.fit(train)
    X_scores = clf.negative_outlier_factor_
    print(X_scores)
elif (args.algorithm == 'svm'):
    clf = svm.OneClassSVM(nu=0.1, gamma=0.01)
    clf.fit(train)
elif (args.algorithm == 'cov'):
    clf = EllipticEnvelope(contamination=0.1)
    clf.fit(train)

# Output test results if relevant
if (test is not None):
    results = clf.predict(test)
    num_correct = np.count_nonzero(results + 1)
    print('{}/{} of test data correct {:.2f}'.format(
        num_correct, 
        len(results), 
        num_correct/len(results)
    ))

# Save model
pickle.dump((not args.use_flows, scaler, pca, clf), open(args.model, 'wb'))

end=time.time()
print("Fitting done, took {:.2f}s".format(end - start))

