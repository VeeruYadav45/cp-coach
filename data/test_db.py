import psycopg2

conn = psycopg2.connect(
    dbname="cpcoach",
    user="postgres",
    password="password",  # Replace with your actual password
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
conn.close()