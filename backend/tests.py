# backend/tests/test_scorer.py
from scorer import compute_skill_scores

def test_perfect_score():
    stats = [{"tag": "math", "attempted": 30, "solved": 30, "accuracy": 100.0}]
    result = compute_skill_scores(stats)
    assert result[0]["score"] == 100.0

def test_zero_accuracy():
    stats = [{"tag": "dp", "attempted": 10, "solved": 0, "accuracy": 0.0}]
    result = compute_skill_scores(stats)
    assert result[0]["score"] < 20  # low volume, zero accuracy

def test_sorted_descending():
    stats = [
        {"tag": "easy", "attempted": 5, "solved": 5, "accuracy": 100.0},
        {"tag": "hard", "attempted": 1, "solved": 0, "accuracy": 0.0},
    ]
    result = compute_skill_scores(stats)

    assert result[0]["tag"] == "easy"
from scorer import compute_skill_scores
from recommender import recommend_problems

def test_perfect_score():
    stats = [{"tag": "math", "attempted": 30, "solved": 30, "accuracy": 100.0}]
    result = compute_skill_scores(stats)
    assert result[0]["score"] == 100.0

def test_zero_accuracy():
    stats = [{"tag": "dp", "attempted": 10, "solved": 0, "accuracy": 0.0}]
    result = compute_skill_scores(stats)
    assert result[0]["score"] < 20  # low volume, zero accuracy

def test_sorted_descending():
    stats = [
        {"tag": "easy", "attempted": 5, "solved": 5, "accuracy": 100.0},
        {"tag": "hard", "attempted": 1, "solved": 0, "accuracy": 0.0},
    ]
    result = compute_skill_scores(stats)
    assert result[0]["tag"] == "easy"

def test_recommends_weak_topic_first():
    problems = [
        {"id": 1, "contest_id": 100, "problem_index": "A", "name": "Math Problem", "rating": 1200, "tags": ["math"]},
        {"id": 2, "contest_id": 100, "problem_index": "B", "name": "DP Problem", "rating": 1200, "tags": ["dp"]},
    ]
    # Yakurto is weak at 'dp'
    result = recommend_problems(problems, user_rating=1100, weak_tags=["dp"], limit=5)
    assert result[0]["name"] == "DP Problem"
    assert "Targets weak topic: dp" in result[0]["reason"]

def test_skips_unrated_problem():
    problems = [
        {"id": 1, "contest_id": 100, "problem_index": "A", "name": "Unrated Problem", "rating": None, "tags": ["math"]},
    ]
    result = recommend_problems(problems, user_rating=1100, weak_tags=["math"], limit=5)
    assert len(result) == 0

def test_respects_limit():
    problems = [
        {"id": i, "contest_id": 100, "problem_index": chr(65 + i), "name": f"P{i}", "rating": 1200, "tags": ["math"]}
        for i in range(10)
    ]
    result = recommend_problems(problems, user_rating=1100, weak_tags=[], limit=3)
    assert len(result) == 3
