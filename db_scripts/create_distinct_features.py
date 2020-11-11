import psycopg2
import sys
import argparse

db_name = "scada"

parser = argparse.ArgumentParser(description='create distinct features DB script')
parser.add_argument('--recreate', help="drop and create new tables", action='store_true')

args = parser.parse_args()

conn = psycopg2.connect('dbname='+ db_name +' user=mini')
#conn = psycopg2.connect("dbname='scada' user='postgres' host='localhost'")
c = conn.cursor()

if args.recreate: 
    c.execute("DROP TABLE features;")
    c.execute("DROP TABLE features_distinct;")
else:
    c.execute("SELECT * FROM pg_catalog.pg_tables WHERE tablename='features_distinct';")
    if (c.fetchone() != None):
        c.execute("SELECT COUNT(*) FROM features_distinct")
        print("features_distinct exists already exists with {} rows".format(c.fetchone()[0]))
        exit(1)



# TODO columns

c.execute('''
create table features as select (
    'ip_src', 
    'ip_dst', 
    'ip_ttl', 
    'ip_len', 
    'ip_ver', 
    'proto', 
    'mac_src', 
    'mac_dst', 
    'tcp_src_port', 
    'tcp_dst_port', 
    'udp_src_port', 
    'udp_dst_port', 
    'icmp_type', 
    'icmp_code', 
    'arp_op', 
    'arp_psrc', 
    'arp_pdst', 
    'arp_hwsrc', 
    'arp_hwdst', 
    'has_ip', 
    'has_ether', 
    'has_tcp', 
    'has_udp', 
    'has_icmp', 
    'has_arp')
 from packet_feats;
''')
c.execute('''
create table  features_distinct as select distinct * from features;
''')

c.close()
conn.commit()
conn.close()
