import psycopg2
from multiprocessing import Process, Queue
import atexit, os, signal
query1 = "INSERT INTO packet_raw (raw, time) VALUES (%s, %s) RETURNING id"

query2 = "WITH row AS ({}) \
          INSERT INTO packet_feat (id, {}) \
          SELECT id, {} FROM row"

query3 = "WITH row AS ({}) \
          INSERT INTO packet_feat (id) \
          SELECT id FROM row"

def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()

def dbDaemon(queue):
    db = dbDriver()
    # atexit.register(close_db, db)
    def close_db(*args):
        print("Inserting rest of queue")
        while not queue.empty():
            parsed_pkt = queue.get()
            raw_dump = parsed_pkt.pop('raw')
            db.insert_packet(raw_dump, parsed_pkt)
        print("Close gets called")
        db.close()
        exit(0)

    signal.signal(signal.SIGINT, close_db)
    # signal.signal(signal.SIGTSTP, close_db)
    # signal.signal(signal.SIGQUIT, close_db)
    # signal.signal(signal.SIGINFO, close_db)
 
    signal.signal(signal.SIGTERM, close_db)
  
    while True:
        # db = Daemon()
        parsed_pkt = queue.get()
        raw_dump = parsed_pkt.pop('raw')
        db.insert_packet(raw_dump, parsed_pkt)
        # db.close()   


class dbDriver():
    def __init__(self):
        self.conn = psycopg2.connect('dbname=scada user=mini')
        self.cur = self.conn.cursor()
        self.counter = 0
    
    def __del__(self):
        self.close()
    
    # insert packet passed as dictionary, with fields corr. to column names
    def insert_packet(self, raw, features):
        # print("**********Insertion called") 
        subquery = self.cur.mogrify(query1, (raw,features['time']))
        subquery = subquery.decode()

        cols = features.keys()
        if (len(cols) > 0):
            col_names = ", ".join(cols)
            vals = ", ".join(["%({0})s".format(col_name) for col_name in cols])
            self.cur.execute(query2.format(subquery, col_names, vals), features)
        else:
            # if the dict is empty, just insert id
            self.cur.execute(query3.format(subquery))
        
        if  self.counter % 1000 == 0:
            self.conn.commit()
        self.counter += 1
 
    
    def read_one_pkt_raw(self):
        # self.cur.execute("SELECT COUNT(*) FROM packet_raw")
        # print("packet_raw exists already exists with {} rows".format(self.cur.fetchone()[0]))
        self.cur.execute("SELECT * FROM packet_raw")    
        return self.cur.fetchone()
    def read_one_pkt_features(self):
        # self.cur.execute("SELECT COUNT(*) FROM packet_raw")
        # print("packet_raw exists already exists with {} rows".format(self.cur.fetchone()[0]))
        self.cur.execute("SELECT * FROM packet_feat")    
        return self.cur.fetchone()
    def read_all_pkt_raw(self):
        self.cur.execute("SELECT COUNT(*) FROM packet_raw")
        print("packet_raw exists already exists with {} rows".format(self.cur.fetchone()[0]))
        self.cur.execute("SELECT * FROM packet_raw")    
        return self.cur.fetchall()
    def read_all_pkt_features(self):
        self.cur.execute("SELECT COUNT(*) FROM packet_feat")
        print("packet_raw exists already exists with {} rows".format(self.cur.fetchone()[0]))
        self.cur.execute("SELECT * FROM packet_feat")    
        return self.cur.fetchall()

    def close(self):
        print("*****Closing db connection")
        self.cur.close()
        self.conn.commit()
        self.conn.close()
        print("*****Connection has been closed")
