"""Multimodal fusion of emotion signals."""

from typing import Optional
from app.utils.logger import logger


def weighted_fusion(
    facial_score: Optional[float] = None,
    speech_score: Optional[float] = None,
    typing_score: Optional[float] = None,
    weights: Optional[dict] = None
) -> float:
    """
    Fuse multiple emotion signals using weighted averaging.
    
    Args:
        facial_score: Emotion score from facial recognition (0-1)
        speech_score: Emotion score from speech analysis (0-1)
        typing_score: Emotion score from typing behavior (0-1)
        weights: Dict with keys 'facial', 'speech', 'typing' for custom weights
        
    Returns:
        Fused emotion score (0-1)
    """
    # Default weights
    if weights is None:
        weights = {"facial": 0.5, "speech": 0.3, "typing": 0.2}
    
    scores = []
    weights_list = []
    
    if facial_score is not None:
        try:
            s = float(facial_score)
            if 0.0 <= s <= 1.0:
                scores.append(s)
                weights_list.append(weights.get("facial", 0.5))
        except (ValueError, TypeError):
            pass
    
    if speech_score is not None:
        try:
            s = float(speech_score)
            if 0.0 <= s <= 1.0:
                scores.append(s)
                weights_list.append(weights.get("speech", 0.3))
        except (ValueError, TypeError):
            pass
    
    if typing_score is not None:
        try:
            s = float(typing_score)
            if 0.0 <= s <= 1.0:
                scores.append(s)
                weights_list.append(weights.get("typing", 0.2))
        except (ValueError, TypeError):
            pass
    
    # If no valid scores, return neutral
    if not scores:
        logger.debug("No valid scores for fusion, returning neutral 0.5")
        return 0.5
    
    # Normalize weights
    total_weight = sum(weights_list)
    if total_weight == 0:
        return 0.5
    
    # Weighted average
    fused = sum(s * w for s, w in zip(scores, weights_list)) / total_weight
    return float(fused)
