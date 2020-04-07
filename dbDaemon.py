import psycopg2
from multiprocessing import Process, Queue
import atexit, os, signal
query1 = "INSERT INTO packet_raw (raw) VALUES (%s) RETURNING id"
query2 = "INSERT INTO packet_feat (id, {}) VALUES ({}, {})"
query3 = "INSERT INTO packet_feat (id) VALUES (%s)"

def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()

def dbDaemon(queue):
    db = Daemon()
    # atexit.register(close_db, db)
    def close_db(*args):
        while not queue.empty():
            parsed_pkt = queue.get()
            raw_dump = parsed_pkt.pop('raw')
            db.insert_packet(raw_dump, parsed_pkt)
        db.close()

    signal.signal(signal.SIGINT, close_db)
    signal.signal(signal.SIGTSTP, close_db)
    signal.signal(signal.SIGQUIT, close_db)
    # signal.signal(signal.SIGINFO, close_db)
 
    signal.signal(signal.SIGTERM, close_db)
  
    while True:
        # db = Daemon()
        parsed_pkt = queue.get()
        raw_dump = parsed_pkt.pop('raw')
        db.insert_packet(raw_dump, parsed_pkt)
        # db.close()   


class Daemon:
    def __init__(self):
        self.conn = psycopg2.connect('dbname=scada user=mini')
        self.cur = self.conn.cursor()
    
    def __del__(self):
        self.close()
    
    # insert packet passed as dictionary, with fields corr. to column names
    def insert_packet(self, raw, features):
        print("**********Insertion called") 
        self.cur.execute(query1, (raw,));
        pg_id = self.cur.fetchone()[0];
        print("**********pg_id={}".format(pg_id))
        if  pg_id % 100==0:
            self.conn.commit()
            
    
        cols = features.keys()

        if (len(cols) > 0):
            col_names = ", ".join(cols)
            vals = ", ".join(["%({0})s".format(col_name) for col_name in cols])
            self.cur.execute(query2.format(col_names, pg_id, vals), features)
        else:
            # if the dict is empty, just insert id
            self.cur.execute(query3, (pg_id,))
    
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
