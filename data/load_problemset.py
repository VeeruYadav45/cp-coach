import json
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path

# Load DB credentials from backend/.env
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "cpcoach"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
)
cur = conn.cursor()

print("Reading problemset.json...")
with open("problemset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

problems_data = data.get("result", {}).get("problems", [])
print(f"Total problems to process: {len(problems_data)}")

# 1. Collect and insert all unique tags first (there are only ~36 distinct tags in CF)
all_tags = set()
for p in problems_data:
    for tag in p.get("tags", []):
        all_tags.add(tag)

tag_rows = [(tag,) for tag in all_tags]
execute_values(
    cur,
    "INSERT INTO tags (name) VALUES %s ON CONFLICT (name) DO NOTHING;",
    tag_rows
)
conn.commit()
print(f"Inserted {len(all_tags)} distinct tags.")

# 2. Batch insert problems (skip any without contestId or index)
problem_rows = []
for p in problems_data:
    contest_id = p.get("contestId")
    problem_index = p.get("index")
    name = p.get("name")
    rating = p.get("rating")  # can be None for unrated/old contests

    if contest_id and problem_index:
        problem_rows.append((contest_id, problem_index, name, rating))

execute_values(
    cur,
    """
    INSERT INTO problems (contest_id, problem_index, name, rating)
    VALUES %s
    ON CONFLICT (contest_id, problem_index)
    DO UPDATE SET rating = EXCLUDED.rating, name = EXCLUDED.name;
    """,
    problem_rows
)
conn.commit()
print(f"Upserted {len(problem_rows)} problems into database.")

# 3. Create mapping caches in memory for fast tag linking
cur.execute("SELECT id, contest_id, problem_index FROM problems;")
problem_id_map = {(row[1], row[2]): row[0] for row in cur.fetchall()}

cur.execute("SELECT id, name FROM tags;")
tag_id_map = {row[1]: row[0] for row in cur.fetchall()}

# 4. Batch insert problem_tags join table
problem_tag_rows = []
for p in problems_data:
    cid = p.get("contestId")
    idx = p.get("index")
    pid = problem_id_map.get((cid, idx))
    if not pid:
        continue
    for t_name in p.get("tags", []):
        tid = tag_id_map.get(t_name)
        if tid:
            problem_tag_rows.append((pid, tid))

execute_values(
    cur,
    "INSERT INTO problem_tags (problem_id, tag_id) VALUES %s ON CONFLICT DO NOTHING;",
    problem_tag_rows
)
conn.commit()
print(f"Linked {len(problem_tag_rows)} problem-tag relationships.")

cur.close()
conn.close()
print("🎉 Problemset import complete!")
