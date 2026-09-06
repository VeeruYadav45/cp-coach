import psycopg2

conn = psycopg2.connect(
    dbname="cpcoach",
    user="postgres",
    password="YOUR_ACTUAL_PASSWORD_HERE",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
conn.close()