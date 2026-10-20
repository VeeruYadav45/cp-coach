# backend/scorer.py

def compute_skill_scores(stats: list[dict]) -> list[dict]:
    """
    Takes the raw stats (tag, attempted, solved, accuracy)
    and returns enriched dicts with a 'score' field added.
    """
    scored = []
    for item in stats:
        accuracy = item["accuracy"]          # already 0-100
        volume = min(item["attempted"], 30)  # cap at 30 so it doesn't dominate
        volume_score = (volume / 30) * 100   # normalize to 0-100

        score = round(
            accuracy * 0.5 +
            volume_score * 0.5,
            1
        )

        scored.append({**item, "score": score})

    return sorted(scored, key=lambda x: x["score"], reverse=True)
