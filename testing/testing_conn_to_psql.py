import psycopg
import pandas as pd
from sqlalchemy import create_engine 
import os
import numpy as np 

print(os.getcwd())


conn = psycopg.connect("dbname=rugby user=postgres password=postgresBen")
cur = conn.cursor()

df = pd.read_csv("app/raw_scores.csv")

for i,v in df.iterrows():

    one_row = v.values.tolist()
    one_row = tuple(one_row)

    cur.execute(f"INSERT INTO match_results\
                  VALUES {one_row};")

conn.commit()
conn.close()

