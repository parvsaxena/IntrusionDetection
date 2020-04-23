import pickle
from multiprocessing import queue
from __init__ import *
import psycopg2
from psycopg2.extras import DictCursor



def lorDaemon(queue):
    conn=psycopg2.connect('dbname={} user=mini'.format("scada"))

    col_cursor = conn.cursor()
    col_query = "select column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'per_packet';"
    col_cursor.execute(col_query)
    columns=col_cursor.fetchall()
    col_cursor.close()
    fields={}
    for index,col in enumerate(columns):
        f=col[0]
        fields[index]=f
    print(fields.values())
    
    pkl_filename="lor_basic_model.pkl"
    with open(pkl_filename, 'rb') as file:
        clf = pickle.load(file)
    
    while True:
        row=queue.get()
        vals=transform(row,fields)
        vec=test_vec(vals)
        prediction=clf.predict()
        if prediction==-1:
            print(prediction, row[id])
