import psycopg
from config import postgres_conn_str

def write_to_postgres_table(df, table):
    print(f"Attempting to write data to {table}")
    try:
        print("Opening connection")
        with psycopg.connect(postgres_conn_str) as conn: # postgres_conn_str is unique to your own user and database
            print("Creating cursor")
            cur = conn.cursor()

            # iterate over dataframe and insert one row at a time
            for i,v in df.iterrows():

                one_row = v.values.tolist()
                one_row = tuple(one_row)

                cur.execute(f"INSERT INTO {table} VALUES {one_row};")

            print("Committing insert")
            conn.commit()

            print("Closing connection")
            conn.close()


    except Exception as e:
        print(f"Fail, could not write to {table}")
        print(e)

