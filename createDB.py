import psycopg2
import sys

conn = psycopg2.connect('dbname=scada user=mini');
c = conn.cursor();

c.execute('''
SELECT * FROM pg_catalog.pg_tables WHERE tablename='packets';
''')

if (c.fetchone() != None):
    c.execute("SELECT COUNT(*) FROM packets")
    print("table exists alread exists with {} rows".format(c.fetchone()[0]))
    exit(1)

# TODO columns
c.execute('''
CREATE TABLE packets (
    id INTEGER,
    time TIMESTAMP,
    raw TEXT
);
''')
