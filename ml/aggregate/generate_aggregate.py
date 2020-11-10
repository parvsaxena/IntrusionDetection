import argparse
import math
import psycopg2
from psycopg2.extras import DictCursor

from datetime import datetime

from BucketCollection import *

# This script reads from the table of packet_features (i.e. packets with parsed header values) and creates
# an "aggregate" object, which is essentially counts of certain features over different time periods.

# Parse command line args
parser = argparse.ArgumentParser(description='Anomaly based intrusion detection baseline generator')
parser.add_argument('--interval', default=60, type=int, help='Bucket interval in seconds')
parser.add_argument('--rowSize', default=60, type=int, help='number of buckets per row of bucket collection')
parser.add_argument('--out', default='buckets.pkl', help='filename of output (pickled object)')

parser.add_argument('--dbName', default='scada', help='name of database to pull statistics from')
parser.add_argument('--dbUsers', default='scada', help='name of database to pull statistics from')
parser.add_argument('--table', default='packet_feat', help='table to look at')

args = parser.parse_args();

# set up db
conn = psycopg2.connect('dbname={} user=mini'.format(args.dbName))
time_cur = conn.cursor()
cur = conn.cursor('cursor', cursor_factory=DictCursor) # server side cursor
# setup the cursor
cur.execute("SELECT * FROM {}".format(args.table))

# get the time of the first packet
time_cur.execute("SELECT time FROM {0} WHERE time = (SELECT MIN(time) FROM {0});".format(args.table))
if (time_cur.rowcount == 0):
    print("No rows in packet_feat!")
    exit(1)
min_time = int(float(time_cur.fetchone()[0]))
time_cur.execute("SELECT time FROM {0} WHERE time = (SELECT MAX(time) FROM {0});".format(args.table))
max_time = int(float(time_cur.fetchone()[0]))
time_cur.close()

total_buckets = (max_time - min_time) // args.interval + 1
stats = BucketCollection(args.interval, total_buckets)

print("Created {} buckets of length {} seconds".format(total_buckets, args.interval))
print("Filling buckets...")

# Start looking at table
for pkt in cur:
    # timestamp in seconds since min_time 
    time = int(float(pkt[1])) - min_time    
    index = time // args.interval
    stats.insert_packet(pkt, index) 
   
stats.print()
stats.save(args.out)

conn.commit()
conn.close()
