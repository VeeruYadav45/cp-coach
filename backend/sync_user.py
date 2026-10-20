# backend/sync_user.py
import requests
from datetime import datetime
import psycopg2

def sync_codeforces_user(handle: str, conn) -> bool:
    """
    Fetches submissions & rating history for `handle` from Codeforces API,
    and inserts them into PostgreSQL. Returns True on success, False if user not found.
    """
    cur = conn.cursor()

    # 1. Fetch from Codeforces API
    status_url = f"https://codeforces.com/api/user.status?handle={handle}"
    rating_url = f"https://codeforces.com/api/user.rating?handle={handle}"

    res_status = requests.get(status_url).json()
    res_rating = requests.get(rating_url).json()

    if res_status.get("status") != "OK":
        cur.close()
        return False  # User probably does not exist on CF

    submissions = res_status.get("result", [])
    rating_history = res_rating.get("result", []) if res_rating.get("status") == "OK" else []

    # 2. Insert or get user_id
    cur.execute(
        "INSERT INTO users (handle) VALUES (%s) ON CONFLICT (handle) DO UPDATE SET handle = EXCLUDED.handle RETURNING id;",
        (handle,)
    )
    user_id = cur.fetchone()[0]

    # 3. Insert submissions
    for sub in submissions:
        prob = sub.get("problem", {})
        contest_id = prob.get("contestId")
        problem_index = prob.get("index")

        if not contest_id or not problem_index:
            continue

        # Look up problem_id from problems table
        cur.execute(
            "SELECT id FROM problems WHERE contest_id = %s AND problem_index = %s;",
            (contest_id, problem_index)
        )
        p_row = cur.fetchone()
        if not p_row:
            # If problem wasn't in problemset, insert minimal record
            cur.execute(
                "INSERT INTO problems (contest_id, problem_index, name, rating) VALUES (%s, %s, %s, %s) RETURNING id;",
                (contest_id, problem_index, prob.get("name"), prob.get("rating"))
            )
            problem_id = cur.fetchone()[0]
        else:
            problem_id = p_row[0]

        verdict = sub.get("verdict")
        lang = sub.get("programmingLanguage")
        creation_time = datetime.fromtimestamp(sub.get("creationTimeSeconds", 0))

        cur.execute(
            """
            INSERT INTO submissions (user_id, problem_id, verdict, programming_language, creation_time, contest_id)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (user_id, problem_id, verdict, lang, creation_time, contest_id)
        )

    # 4. Insert rating history
    for entry in rating_history:
        contest_id = entry.get("contestId")
        contest_name = entry.get("contestName")
        old_rating = entry.get("oldRating")
        new_rating = entry.get("newRating")
        update_time = datetime.fromtimestamp(entry.get("ratingUpdateTimeSeconds", 0))

        cur.execute(
            """
            INSERT INTO rating_history (user_id, contest_id, contest_name, old_rating, new_rating, rating_update_time)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (user_id, contest_id, contest_name, old_rating, new_rating, update_time)
        )

    conn.commit()
    cur.close()
    return True

