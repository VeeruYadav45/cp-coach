# backend/recommender.py

def recommend_problems(
    unsolved_problems: list[dict],
    user_rating: int,
    weak_tags: list[str],
    limit: int = 5
) -> list[dict]:
    """
    Ranks unattempted/unsolved problems based on:
    1. Difficulty Fit: Sweet spot is user_rating to user_rating + 200.
    2. Topic Relevance: Heavy bonus if the problem contains one of the user's weak topics.
    """
    target_rating = user_rating if user_rating > 0 else 1000
    candidates = []

    for prob in unsolved_problems:
        rating = prob.get("rating")
        if rating is None:
            continue  # skip unrated problems

        tags = prob.get("tags", [])
        
        # 1. Difficulty score (0 to 50): Closer to (target_rating + 100) is better
        # Sweet spot is +50 to +150 above current rating
        ideal_rating = target_rating + 100
        diff_distance = abs(rating - ideal_rating)
        difficulty_score = max(0, 50 - (diff_distance / 10))

        # 2. Topic gap score (0 to 50):
        # Checks how many of the user's weak tags this problem exercises
        matching_weak_tags = [t for t in tags if t in weak_tags]
        topic_score = min(50, len(matching_weak_tags) * 25)

        total_score = round(difficulty_score + topic_score, 1)

        # Build clean direct Codeforces link
        contest_id = prob["contest_id"]
        problem_index = prob["problem_index"]
        url = f"https://codeforces.com/contest/{contest_id}/problem/{problem_index}"

        # Explanation for the user
        reasons = []
        if matching_weak_tags:
            reasons.append(f"Targets weak topic: {', '.join(matching_weak_tags)}")
        if abs(rating - target_rating) <= 150:
            reasons.append(f"Matches your target rating ({rating})")

        reason_text = " • ".join(reasons) if reasons else f"Good rating match ({rating})"

        candidates.append({
            "id": prob["id"],
            "contest_id": contest_id,
            "problem_index": problem_index,
            "name": prob["name"],
            "rating": rating,
            "tags": tags,
            "url": url,
            "match_score": total_score,
            "reason": reason_text,
        })

    # Sort highest recommendation score first
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:limit]
