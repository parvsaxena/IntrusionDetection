import argparse
import psycopg2
from psycopg2.extras import DictCursor

from datetime import datetime

from anomalyStats import *

parser = argparse.ArgumentParser(description='Anomaly based intrusion detection baseline generator')
parser.add_argument('--interval', default=60, type=int, help='overall interval to collect in minutes')
parser.add_argument('--buckets', default=60, type=int, help='number of buckets over interval to aggregate stats in')
parser.add_argument('--dbName', default='scada', help='overall interval to collect in minutes')

args = parser.parse_args();

conn = psycopg2.connect('dbname={} user=mini'.format(args.dbName))
cur = conn.cursor('cursor', cursor_factory=DictCursor) # server side cursor
cur.execute("SELECT * FROM packet_feat")

n = args.buckets
bucketInterval = args.interval / args.buckets # time that one bucket represents

stats = AnomalyStats(n)
curBucket = Bucket()

prevIndex = n

for row in cur:
    # timestamp in seconds since epoch
    time = int(float(row[1])) 

    # which bucket the packet belongs to 
    index = int((time % (60 * args.interval)) // (60 * bucketInterval))
    
    if (index != prevIndex and prevIndex != n):
        stats.addToAvg(prevIndex, curBucket)
        curBucket = Bucket()

    curBucket.update(row)
    prevIndex = index
   
stats.print()

conn.commit()
conn.close()
