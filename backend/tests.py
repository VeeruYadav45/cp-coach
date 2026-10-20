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
