import argparse
import psycopg2
from psycopg2.extras import DictCursor

from datetime import datetime

from PacketAggregate import *

'''
This script reads from the table of packet_features (i.e. packets with parsed header values) and creates
an "aggregate" object, which is essentially counts of certain features over different time periods.
'''


# Parse command line args
parser = argparse.ArgumentParser(description='Anomaly based intrusion detection baseline generator')
parser.add_argument('--interval', default=60, type=int, help='overall interval to collect in minutes')
parser.add_argument('--buckets', default=60, type=int, help='number of buckets over interval to aggregate stats in')
parser.add_argument('--dbName', default='scada', help='name of database to pull statistics from')
parser.add_argument('--statsFile', default='baseline.out', help='filename of output (pickled object)')
parser.add_argument('--table', default='packet_feat', help='table to look at')

args = parser.parse_args();
# convert interval to seconds
args.interval = 60 * args.interval


# set up db
conn = psycopg2.connect('dbname={} user=mini'.format(args.dbName))
firstCur = conn.cursor()
cur = conn.cursor('cursor', cursor_factory=DictCursor) # server side cursor
# setup the cursor
cur.execute("SELECT * FROM {}".format(args.table))

# get the time of the first packet
firstCur.execute("SELECT time FROM {0} WHERE time = (SELECT MIN(time) FROM {0});".format(args.table))
if (firstCur.rowcount == 0):
    print("No rows in packet_feat!")
    exit(1)
minTime = int(float(firstCur.fetchone()[0]))
firstCur.execute("SELECT time FROM {0} WHERE time = (SELECT MAX(time) FROM {0});".format(args.table))
maxTime = int(float(firstCur.fetchone()[0]))
firstCur.close()

# round minTime/maxTime to nearest interval
minTime = (minTime // (args.interval)) * args.interval
maxTime = (maxTime // (args.interval)) * args.interval


# m is number of total intervals (ie. hours by default), nubmer of buckets at each slot
# n is number of bukcet per interval 
# time that one bucket represents
# our data is an m x n array of buckets
m = 1 + (maxTime - minTime) // args.interval
n = args.buckets
bucketInterval = args.interval / args.buckets
stats = PacketAggregate(args.interval, m, n)

print("constants")
print(m, n, bucketInterval, stats)

# Start looking at table
prevIndex = -1
firstBucket = True
iterations = 0

for row in cur:
    # timestamp in seconds since minTime 
    time = int(float(row[1])) - minTime    
    index = int(time / bucketInterval)

    # update appropriate packet
    stats.update(row, index) 
   
stats.print()
stats.save(args.statsFile)

conn.commit()
conn.close()
