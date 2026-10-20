import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "cpcoach"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
)
cur = conn.cursor()
#id SERIAL PRIMARY KEY-this is a column that will automatically generate unique integer values for each row and will be used as the primary key for the table
#Unique-no two rows can have the same handele
#records when the row was inserted; DEFAULT NOW() means if you don't specify a value, Postgres automatically fills in the current date/time.
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    handle TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
""")#send a raw sql command to database to create table if not exists with given columns and constraints

cur.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    contest_id INTEGER,
    problem_index TEXT,
    name TEXT,
    rating INTEGER,
    UNIQUE (contest_id, problem_index)
);
""")
#Simple lookup table — one row per distinct tag name
cur.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS problem_tags (
    problem_id INTEGER REFERENCES problems(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (problem_id, tag_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    problem_id INTEGER REFERENCES problems(id),
    verdict TEXT,
    programming_language TEXT,
    creation_time TIMESTAMP,
    contest_id INTEGER
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS rating_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    contest_id INTEGER,
    contest_name TEXT,
    old_rating INTEGER,
    new_rating INTEGER,
    rating_update_time TIMESTAMP
);
""")

conn.commit()#to save to the database all the changes made in the current transaction. If you don't call commit(), the changes will not be saved and will be lost when the connection is closed.
print("All tables created successfully.")

cur.close()#to free up resources and avoid potential memory leaks. It is a good practice to close the cursor when it is no longer needed.
conn.close()