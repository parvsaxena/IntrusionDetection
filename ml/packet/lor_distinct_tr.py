import numpy as np
import time
import psycopg2
from psycopg2.extras import DictCursor
from  __init__ import *
import pickle
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler




if  __name__=='__main__':
    start=time.time()
    
    conn=psycopg2.connect('dbname={} user=mini'.format("scada"))
    """
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
    """
    fields2={}
    for index,col in enumerate(distinct_cols):
        fields2[index]=col
    print(fields2.values())


    cur = conn.cursor('cursor', cursor_factory=DictCursor) # server side cursor
    # cur.execute("SELECT  * FROM distinct_feat LIMIT 5;")
    cur.execute("SELECT distinct * FROM per_packet;")
    vecs=[]
    for row in cur:
        vec=row
        vecs.append(vec)
        print(vec)
    scaler=StandardScaler()
    #scaler=MinMaxScaler()
    scaler.fit(vecs)
    vecs=scaler.transform(vecs)
    end=time.time()
    conn.close()
    print(end-start)   
    print(len(vecs))
    for vec in vecs:
        print(vec)
    start=time.time()
    clf=LocalOutlierFactor(n_neighbors=1,novelty=True,metric='cosine')
    clf.fit(vecs)
    print("Fitting done")
    pkl_filename = "lor_distinct_model.pkl"
    pickle.dump(clf, open(pkl_filename, 'wb'))
    pkl_scaler = "lor_scaler.pkl"
    pickle.dump(scaler, open(pkl_scaler, 'wb'))
    end=time.time()
    # print(end-start) 
  
    
    X_scores = clf.negative_outlier_factor_
    print(X_scores)
    '''
    plt.title("Local Outlier Factor (LOF)")
    plt.scatter(X[:, 0], X[:, 1], color='k', s=3., label='Data points')
    # plot circles with radius proportional to the outlier scores
    radius = (X_scores.max() - X_scores) / (X_scores.max() - X_scores.min())
    plt.scatter(X[:, 0], X[:, 1], s=1000 * radius, edgecolors='r',facecolors='none', label='Outlier scores')
    plt.axis('tight')
    plt.xlim((-5, 5))
    plt.ylim((-5, 5))
    legend = plt.legend(loc='upper left')
    legend.legendHandles[0]._sizes = [10]
    legend.legendHandles[1]._sizes = [20]
    plt.show()
    '''
       
