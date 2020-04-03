import psycopg2


query1 = "INSERT INTO packet_raw (raw) VALUES (%s) RETURNING id"
query2 = "INSERT INTO packet_feat (id, {}) VALUES ({}, {})"
query3 = "INSERT INTO packet_feat (id) VALUES (%s)"

def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()


class Daemon:
    def __init__(self):
        self.conn = psycopg2.connect('dbname=scada user=mini')
        self.cur = self.conn.cursor()
    
    # insert packet passed as dictionary, with fields corr. to column names
    def insert_packet(self, raw, features):

        self.cur.execute(query1, (raw,));
        pg_id = self.cur.fetchone()[0];
    
        cols = features.keys()

        if (len(cols) > 0):
            col_names = ", ".join(cols)
            vals = ", ".join(["%({0})s".format(col_name) for col_name in cols])
            self.cur.execute(query2.format(col_names, pg_id, vals), features)
        else:
            # if the dict is empty, just insert id
            self.cur.execute(query3, (pg_id,))
    
    def read_one_pkt(self):
        self.cur.execute("SELECT * FROM packet_raw")    
        return self.cur.fetchone()

    def close(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()
