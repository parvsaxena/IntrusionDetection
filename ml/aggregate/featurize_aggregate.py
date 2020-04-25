import sys

import argparse
import numpy as np

import pickle
import sklearn.preprocessing

# get the set of known/unknown labels for udp fields by seeing which
# values are common across all buckets
def get_common_labels(baseline):
    labels = {
        'udp_port': set(),
        'udp_len': set()
    }
    
    first = True

    for b in baseline:
        counts = b.categoryCounts
        ports = counts['udp_src_port'].keys() | counts['udp_dst_port'].keys()
        lens = counts['udp_len'].keys()
        
        if (first):
            first = False
            labels['udp_port'] = ports
            labels['udp_len'] = lens
        else:
            labels['udp_port'] &= ports
            labels['udp_len'] &= lens

    return {k : list(v) for k, v in labels.items()}


def place_feature(known, feature, value, row_section):
    if (feature in known):
        row_section[known.index(feature)] = value
    # Other
    else:
        row_section[len(known)] += value
        
def get_feature_names(known, bucket):
    names = []
    names.append('total')
    names += [field for field in bucket.pktCounts]

    for field, counts in bucket.categoryCounts.items():
        section = []
        feat = None
        if (field == 'ip_src' or field == 'ip_dst'):
            section = [field + '/' + feat for feat in known['ip']]
        if (field == 'mac_src' or field == 'mac_dst'):
            section = [field + '/' + feat for feat in known['mac']]
        if (field == 'udp_src_port' or field == 'udp_dst_port'):
            section = [field + '/' + str(feat) for feat in known['udp_port']]
        if (field == 'udp_len'):
            section = [field + '/' + str(feat) for feat in known['udp_len']]
        names += section + [field + '/other']

    return names


# Converts a bucket of packet counts into a feature vector, given a list of known
# ips, macs, udp ports and lens. (counts other lengths as 'other')
def featurize(known, bucket):
    row = []

    row.append(bucket.total)
    row += [count for field, count in sorted(bucket.pktCounts.items())]

    for field, counts in sorted(bucket.categoryCounts.items()):
        row_section = None
        known_vals = None

        if (field == 'ip_src' or field == 'ip_dst'):
            known_vals = known['ip']
            row_section = [0 for i in range(len(known['ip']) + 1)]
        if (field == 'mac_src' or field == 'mac_dst'):
            known_vals = known['mac']
            row_section = [0 for i in range(len(known['mac']) + 1)]
        if (field == 'udp_src_port' or field == 'udp_dst_port'):
            known_vals = known['udp_port']
            row_section = [0 for i in range(len(known['udp_port']) + 1)]
        if (field == 'udp_len'):
            known_vals = known['udp_len']
            row_section = [0 for i in range(len(known['udp_len']) + 1)]
        
        if (row_section == None):
            raise Exception("Error: known values for field {} not present!".format(field))
    
        for feature, cnt in counts.items():
            place_feature(known_vals, feature, cnt, row_section)
        
        row += (row_section)
    return row
            

if __name__ == "__main__":

    # Parse command line args
    parser = argparse.ArgumentParser(description='Generate feature vector from vector of baseline measurements')
    parser.add_argument('--baseline', default='./baseline.out', help='pickled baseline object')
    parser.add_argument('--output', default='./aggregate_features.pkl', help='pickled baseline object')

    args = parser.parse_args();

    # Define known settings ips and mac addresses
    ips = [
        '128.220.221.91',
        '128.220.221.92', 
        #'128.220.221.93', 
        '128.220.221.94',
        '128.220.221.95', 
        '128.220.221.96',
        # '128.220.221.15',
        '128.220.221.16',
        '128.220.221.17'
    ]

    macs = [
        '00:22:4d:b8:6f:04',
        '00:22:4d:b8:6f:a5',
        #['', 4546] 
        '00:22:4d:b8:70:0c',
        '00:22:4d:d0:88:58',
        '00:22:4d:d0:88:74',
        # ['00:22:4d:b5:86:75', 4546],
        '00:22:4d:b5:86:8b',
        '00:22:4d:b5:86:67'
    ]

    f = open(args.baseline, "rb")
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
    
    # build features
    known = get_common_labels(bkts)
    known['ip'] = ips
    known['mac'] = macs

    #print(known)

    # build array
    data = []
    for b in bkts:
        data.append(featurize(known, b))
    
    data = np.array(data)
    data = sklearn.preprocessing.normalize(data)
    names = get_feature_names(known, bkts[0])

    print(names)
    print(len(names))
    print("number of data points:", len(data))
    print(data)
    # save array
    with open(args.output, "wb") as f:
        pickle.dump((known, names, data), f)
