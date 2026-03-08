"""
Facial emotion inference wrapper.
Delegates to FacialEmotionModel which handles CNN weights or heuristic fallback.
"""
from typing import Optional
from app.utils.logger import logger
from .model import FacialEmotionModel

try:
    import numpy as np
except Exception:
    np = None

facial_model = FacialEmotionModel()


def predict_emotion_score(image_array: Optional["np.ndarray"] = None) -> float:
    """
    Predict emotion score from image array.
    Returns float in [0.0, 1.0].
    """
    try:
        return facial_model.predict(image_array)
    except Exception as e:
        logger.warning(f"Facial prediction failed: {e}, returning neutral")
        return 0.5

