from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv
from scorer import compute_skill_scores
from recommender import recommend_problems

load_dotenv()  # reads backend/.env into environment variables

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "cpcoach"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stats/{handle}")
def get_stats(handle: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            t.name AS tag,
            COUNT(DISTINCT p.id) AS attempted,
            COUNT(DISTINCT CASE WHEN s.verdict = 'OK' THEN p.id END) AS solved
        FROM tags t
        JOIN problem_tags pt ON pt.tag_id = t.id
        JOIN problems p ON p.id = pt.problem_id
        JOIN submissions s ON s.problem_id = p.id
        JOIN users u ON u.id = s.user_id
        WHERE u.handle = %s
        GROUP BY t.name
        ORDER BY attempted DESC;
    """, (handle,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for tag, attempted, solved in rows:
        result.append({
            "tag": tag,
            "attempted": attempted,
            "solved": solved,
            "accuracy": round(solved / attempted * 100, 1) if attempted else 0
        })

    return {"handle": handle, "stats": result}


@app.get("/score/{handle}")
def get_score(handle: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            t.name AS tag,
            COUNT(DISTINCT p.id) AS attempted,
            COUNT(DISTINCT CASE WHEN s.verdict = 'OK' THEN p.id END) AS solved
        FROM tags t
        JOIN problem_tags pt ON pt.tag_id = t.id
        JOIN problems p ON p.id = pt.problem_id
        JOIN submissions s ON s.problem_id = p.id
        JOIN users u ON u.id = s.user_id
        WHERE u.handle = %s
        GROUP BY t.name
        ORDER BY attempted DESC;
    """, (handle,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    stats = [
        {
            "tag": tag,
            "attempted": attempted,
            "solved": solved,
            "accuracy": round(solved / attempted * 100, 1) if attempted else 0,
        }
        for tag, attempted, solved in rows
    ]

    scored = compute_skill_scores(stats)
    return {"handle": handle, "scores": scored}


@app.get("/recommend/{handle}")
def get_recommendations(handle: str, limit: int = 5):
    conn = get_connection()
    cur = conn.cursor()

    # 1. Fetch user's current rating from rating_history
    cur.execute("""
        SELECT rh.new_rating
        FROM rating_history rh
        JOIN users u ON u.id = rh.user_id
        WHERE u.handle = %s
        ORDER BY rh.rating_update_time DESC
        LIMIT 1;
    """, (handle,))
    rating_row = cur.fetchone()
    user_rating = rating_row[0] if rating_row and rating_row[0] else 1000

    # 2. Get user's weak topics (scores < 60, or bottom 3 topics)
    cur.execute("""
        SELECT
            t.name AS tag,
            COUNT(DISTINCT p.id) AS attempted,
            COUNT(DISTINCT CASE WHEN s.verdict = 'OK' THEN p.id END) AS solved
        FROM tags t
        JOIN problem_tags pt ON pt.tag_id = t.id
        JOIN problems p ON p.id = pt.problem_id
        JOIN submissions s ON s.problem_id = p.id
        JOIN users u ON u.id = s.user_id
        WHERE u.handle = %s
        GROUP BY t.name;
    """, (handle,))
    stats_rows = cur.fetchall()
    stats = [
        {
            "tag": tag,
            "attempted": attempted,
            "solved": solved,
            "accuracy": round(solved / attempted * 100, 1) if attempted else 0,
        }
        for tag, attempted, solved in stats_rows
    ]
    scored = compute_skill_scores(stats)
    # Lowest scores are at the end since compute_skill_scores sorts descending
    weak_tags = [item["tag"] for item in scored if item["score"] < 60]
    if not weak_tags and scored:
        weak_tags = [item["tag"] for item in scored[-3:]]

    # 3. Fetch candidate problems not yet solved by this user
    cur.execute("""
        SELECT
            p.id,
            p.contest_id,
            p.problem_index,
            p.name,
            p.rating,
            COALESCE(ARRAY_AGG(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') AS tags
        FROM problems p
        LEFT JOIN problem_tags pt ON pt.problem_id = p.id
        LEFT JOIN tags t ON t.id = pt.tag_id
        WHERE p.rating IS NOT NULL
          AND p.id NOT IN (
              SELECT s.problem_id
              FROM submissions s
              JOIN users u ON u.id = s.user_id
              WHERE u.handle = %s AND s.verdict = 'OK'
          )
        GROUP BY p.id
        ORDER BY p.id DESC
        LIMIT 800;
    """, (handle,))
    problem_rows = cur.fetchall()
    cur.close()
    conn.close()

    candidate_problems = [
        {
            "id": r[0],
            "contest_id": r[1],
            "problem_index": r[2],
            "name": r[3],
            "rating": r[4],
            "tags": r[5],
        }
        for r in problem_rows
    ]

    recommendations = recommend_problems(
        unsolved_problems=candidate_problems,
        user_rating=user_rating,
        weak_tags=weak_tags,
        limit=limit
    )

    return {
        "handle": handle,
        "user_rating": user_rating,
        "weak_tags": weak_tags,
        "recommendations": recommendations,
    }
