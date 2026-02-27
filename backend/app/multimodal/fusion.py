from typing import Optional


def weighted_fusion(facial_score: Optional[float], speech_score: Optional[float], typing_score: Optional[float], weights=None) -> float:
    weights = weights or {"facial": 0.5, "speech": 0.3, "typing": 0.2}
    total_weight = 0.0
    score = 0.0
    if facial_score is not None:
        score += facial_score * weights.get("facial", 0.0)
        total_weight += weights.get("facial", 0.0)
    if speech_score is not None:
        score += speech_score * weights.get("speech", 0.0)
        total_weight += weights.get("speech", 0.0)
    if typing_score is not None:
        score += typing_score * weights.get("typing", 0.0)
        total_weight += weights.get("typing", 0.0)
    if total_weight == 0:
        return 0.5
    return float(score / total_weight)
