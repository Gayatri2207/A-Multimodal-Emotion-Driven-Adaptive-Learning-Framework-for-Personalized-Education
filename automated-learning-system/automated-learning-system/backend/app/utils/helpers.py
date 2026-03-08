def normalize_score(score: float):
    return max(0, min(1, score))

def map_emotion_label(label: int):
    emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    return emotions[label] if label < len(emotions) else "unknown"
