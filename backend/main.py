from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2  

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
    conn = psycopg2.connect(
        dbname="cpcoach",
        user="postgres",
        password="password",  # Replace with your password
        host="localhost",
        port="5432"
    )
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