import psycopg2
import sys

conn = psycopg2.connect('dbname=scada user=mini');
c = conn.cursor();

c.execute('''
SELECT * FROM pg_catalog.pg_tables WHERE tablename='packet_raw';
''')

if (c.fetchone() != None):
    c.execute("SELECT COUNT(*) FROM packet_raw")
    print("packet_raw exists already exists with {} rows".format(c.fetchone()[0]))
    exit(1)

# TODO columns
c.execute('''
CREATE TABLE packet_raw (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP,
    raw TEXT NOT NULL
);
''')

c.execute('''
CREATE TABLE packet_feat (
    id INTEGER,
    time TIMESTAMP,

    ip_src VARCHAR(128),
    ip_dst VARCHAR(128),
    ip_ttl INTEGER,
    ip_len INTEGER,  
    ip_ver INTEGER,
    proto  INTEGER,

    mac_src    VARCHAR(128),
    mac_dst    VARCHAR(128),
    ether_type INTEGER,

    tcp_src_port INTEGER,
    tcp_dst_port INTEGER,

    udp_src_port INTEGER,
    udp_dst_port INTEGER,
    udp_len      INTEGER,
    
    icmp_type     INTEGER,
    icmp_code     INTEGER,
    
    arp_op        INTEGER,
    arp_psrc      VARCHAR(128),
    arp_pdst      VARCHAR(128),
    arp_hwsrc     VARCHAR(128),
    arp_hwdst     VARCHAR(128)
);
''')

c.close()
conn.commit()
conn.close()
