import argparse
import psycopg2

from datetime import datetime

from anomalyStats import *

parser = argparse.ArgumentParser(description='Anomaly based intrusion detection baseline generator')
parser.add_argument('--interval', default=60, type=int, help='overall interval to collect in minutes')
parser.add_argument('--resolution', default=1, type=int, help='time period stats are agreggated over, should be factor of interval')
parser.add_argument('--dbName', default='scada', help='overall interval to collect in minutes')

args = parser.parse_args();

if (args.interval % args.resolution != 0):
    print("interval not multiple of resolution!")
    exit(1)


conn = psycopg2.connect('dbname={} user=mini'.format(args.dbName))
cur = conn.cursor('cursor') # server side cursor
cur.execute("SELECT * FROM packet_feat")

n = args.interval // args.resolution

avgStats = AnomalyStats(n)
curStats = newStats()

prevIndex = n

count = 0
for row in cur:
    # timestamp in seconds since epoch
    time = int(float(row[1])) 

    # which period the packet belongs to 
    index = (time % (60 * args.interval)) // (60 * args.resolution)
    
    if (index != prevIndex and prevIndex != n):
        avgStats.addToAvg(prevIndex, curStats)
        curStats = newStats()

    updateStats(curStats, row)
    prevIndex = index
   
avgStats.save()

conn.commit()
conn.close()
