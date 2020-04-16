import argparse
import psycopg2
from psycopg2.extras import DictCursor

from datetime import datetime

from anomalyStats import *

parser = argparse.ArgumentParser(description='Anomaly based intrusion detection baseline generator')
parser.add_argument('--interval', default=60, type=int, help='overall interval to collect in minutes')
parser.add_argument('--buckets', default=60, type=int, help='number of buckets over interval to aggregate stats in')
parser.add_argument('--dbName', default='scada', help='name of database to pull statistics from')
parser.add_argument('--statsFile', default='baseline.out', help='filename of output (pickled object)')
parser.add_argument('--limit', default=-1, type=int, help='limit on the number of bukcets to go over')

args = parser.parse_args();

conn = psycopg2.connect('dbname={} user=mini'.format(args.dbName))
cur = conn.cursor('cursor', cursor_factory=DictCursor) # server side cursor
cur.execute("SELECT * FROM packet_feat")

n = args.buckets
bucketInterval = args.interval / args.buckets # time that one bucket represents

stats = AnomalyStats(args.interval, n)
curBucket = Bucket()

prevIndex = n
firstBucket = True

iterations = 0

for row in cur:
    # timestamp in seconds since epoch
    time = int(float(row[1])) 
    # time = datetime.fromtimestamp(timestamp)

    # TODO: convert timestamp to time to place it in correct minute bucket
    # which bucket the packet belongs to 
    index = int((time % (60 * args.interval)) // (60 * bucketInterval))
    
    if (index != prevIndex and prevIndex != n):
        if (not firstBucket): 
            print("Inserting into bucket {}".format(index))
            if (iterations >= args.limit and args.limit != -1): 
                break
            stats.addToAvg(prevIndex, curBucket)
            iterations += 1
        else: 
            firstBucket = False
        curBucket = Bucket()


    curBucket.update(row)
    prevIndex = index
   
stats.print()
stats.save(args.statsFile)

conn.commit()
conn.close()
