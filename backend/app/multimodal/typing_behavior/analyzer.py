from typing import List
import numpy as np


class TypingBehaviorAnalyzer:
    def __init__(self):
        pass

    def analyze(self, keystroke_intervals: List[float], mistakes: int, total_chars: int) -> float:
        if not keystroke_intervals:
            speed_score = 0.5
        else:
            avg_interval = float(np.mean(keystroke_intervals))
            # faster typing -> lower interval -> higher score
            speed_score = max(0.0, min(1.0, 1.0 - (avg_interval / 0.5)))
        if total_chars <= 0:
            accuracy_score = 0.5
        else:
            accuracy_score = max(0.0, min(1.0, 1.0 - (mistakes / total_chars)))
        # weighted
        return float(0.6 * accuracy_score + 0.4 * speed_score)
import time

class TypingBehaviorAnalyzer:

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self, characters_typed):
        if not self.start_time:
            return 0

        elapsed = time.time() - self.start_time
        typing_speed = characters_typed / elapsed if elapsed > 0 else 0
        return typing_speed

    def classify_behavior(self, typing_speed):
        if typing_speed < 2:
            return "frustrated"
        elif typing_speed > 6:
            return "engaged"
        else:
            return "neutral"
