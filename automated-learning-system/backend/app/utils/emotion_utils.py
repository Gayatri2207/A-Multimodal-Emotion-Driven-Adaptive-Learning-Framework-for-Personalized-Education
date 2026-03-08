def get_emotion_label(score: float) -> str:
    """Convert a numeric emotion score (0–1) to a human-readable label."""
    if score < 0.20:
        return "Frustrated"
    if score < 0.35:
        return "Struggling"
    if score < 0.50:
        return "Neutral"
    if score < 0.65:
        return "Focused"
    if score < 0.80:
        return "Engaged"
    return "Excited"
