import psycopg2
from multiprocessing import Process, Queue
import os, signal

query1 = "INSERT INTO packet_raw (raw, time, is_training) VALUES (%s, %s, %s) RETURNING id"

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

def db_insertion_daemon(queue, dbName="scada"):
    db = dbDriver(dbName)
    print("Daemon created")

    def close_db(*args):
        print("Inserting rest of queue")
        while not queue.empty():
            parsed_pkt = queue.get()
            raw_dump = parsed_pkt.pop('raw')
            db.insert_packet(raw_dump, parsed_pkt)
        print("Closing ")
        db.close()
        exit(0)

    signal.signal(signal.SIGINT, close_db)
    signal.signal(signal.SIGTERM, close_db)
  
    while True:
        parsed_pkt = queue.get()
        raw_dump = parsed_pkt.pop('raw')
        db.insert_packet(raw_dump, parsed_pkt)


class dbDriver():
    def __init__(self, dbName):
        self.conn = psycopg2.connect("dbname={} user='mini' host='localhost'".format(dbName))
        self.cur = self.conn.cursor()
        self.counter = 0
    
    def __del__(self):
        self.close()
    
    # insert packet passed as dictionary, with fields corr. to column names
    def insert_packet(self, raw, features, retry=False):
        try:
            subquery = self.cur.mogrify(query1, (raw, features['time'], features['is_training']))
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

        except psycopg2.InterfaceError:
            # Attempt to reopen pointer
            self.cur.close()    
            self.cur = conn.cursor()
            self.insert_packet(raw, features, True)
   
    def read_one_pkt_raw(self):
        self.cur.execute("SELECT * FROM packet_raw")    
        return self.cur.fetchone()
    def read_one_pkt_features(self):
        self.cur.execute("SELECT * FROM packet_feat")    
        return self.cur.fetchone()
    def read_all_pkt_raw(self):
        self.cur.execute("SELECT * FROM packet_raw")    
        return self.cur.fetchall()
    def read_all_pkt_features(self):
        self.cur.execute("SELECT * FROM packet_feat")    
        return self.cur.fetchall()
    
    def read_raw_by_id(self, id):
        self.cur.execute("SELECT * FROM packet_raw where id=" + str(id))
        return self.cur.fetchone()

    def close(self):
        print("*****Closing db connection")
        self.cur.close()
        self.conn.commit()
        self.conn.close()
