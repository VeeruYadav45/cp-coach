import json
import psycopg2
from datetime import datetime

HANDLE = "Yakurto"  # my actual handle(replace with yours)

conn = psycopg2.connect(
    dbname="cpcoach",
    user="postgres",
    password="password",  # Replace with your  password
    host="localhost",
    port="5432"
)
cur=conn.cursor()
#inserts the handle into user table
cur.execute(
    "INSERT INTO users (handle) VALUES (%s) ON CONFLICT (handle) DO NOTHING RETURNING id;",
    (HANDLE,)
)
#fetchone() this grabs the id if insert happened 
result = cur.fetchone()
if result:
    user_id = result[0]
else:
    cur.execute("SELECT id FROM users WHERE handle = %s;", (HANDLE,))
    user_id = cur.fetchone()[0]

with open("submissions.json") as f:
    submissions_data = json.load(f)["result"]

with open("rating_history.json") as f:
    rating_data = json.load(f)["result"]

print(f"User ID: {user_id}")
print(f"Loaded {len(submissions_data)} submissions, {len(rating_data)} rating entries from JSON")
for sub in submissions_data:
    problem = sub["problem"]
    contest_id = problem.get("contestId")
    problem_index = problem.get("index")
    name = problem.get("name")
    rating = problem.get("rating")  # may be None if unrated

    cur.execute(
        """
        INSERT INTO problems (contest_id, problem_index, name, rating)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (contest_id, problem_index) DO NOTHING
        RETURNING id;
        """,
        (contest_id, problem_index, name, rating)
    )
    result = cur.fetchone()
    if result:
        problem_id = result[0]
    else:
        cur.execute(
            "SELECT id FROM problems WHERE contest_id = %s AND problem_index = %s;",
            (contest_id, problem_index)
        )
        problem_id = cur.fetchone()[0]
    tags = problem.get("tags", [])
    for tag_name in tags:
        cur.execute(
            "INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;",
            (tag_name,)
        )
        tag_result = cur.fetchone()
        if tag_result:
            tag_id = tag_result[0]
        else:
            cur.execute("SELECT id FROM tags WHERE name = %s;", (tag_name,))
            tag_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (problem_id, tag_id)
        )

    verdict = sub.get("verdict")
    language = sub.get("programmingLanguage")
    creation_time = datetime.fromtimestamp(sub["creationTimeSeconds"])
    sub_contest_id = sub.get("contestId")

    cur.execute(
        """
        INSERT INTO submissions (user_id, problem_id, verdict, programming_language, creation_time, contest_id)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (user_id, problem_id, verdict, language, creation_time, sub_contest_id)
    )
for entry in rating_data:
    contest_id = entry.get("contestId")
    contest_name = entry.get("contestName")
    old_rating = entry.get("oldRating")
    new_rating = entry.get("newRating")
    update_time = datetime.fromtimestamp(entry["ratingUpdateTimeSeconds"])

    cur.execute(
        """
        INSERT INTO rating_history (user_id, contest_id, contest_name, old_rating, new_rating, rating_update_time)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (user_id, contest_id, contest_name, old_rating, new_rating, update_time)
    )

conn.commit()
print("All data loaded successfully.")

cur.close()
conn.close()