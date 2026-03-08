"""Typing behavior analysis for emotion inference."""

import time
from typing import List, Optional
import random
from app.utils.logger import logger


class TypingBehaviorAnalyzer:
    """Analyze typing behavior to infer emotion state."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.keystroke_times: List[float] = []
    
    def start_session(self):
        """Start recording typing session."""
        self.start_time = time.time()
        self.keystroke_times = []
    
    def record_keystroke(self):
        """Record a keystroke timestamp."""
        if self.start_time is None:
            self.start_time = time.time()
        self.keystroke_times.append(time.time())
    
    def analyze(
        self,
        keystroke_intervals: Optional[List[float]] = None,
        mistakes: int = 0,
        total_chars: int = 0
    ) -> float:
        """
        Analyze typing behavior and return emotion score.
        
        Args:
            keystroke_intervals: Time intervals between keystrokes
            mistakes: Number of typing mistakes
            total_chars: Total characters typed
            
        Returns:
            Emotion score 0-1
        """
        try:
            # Analyze speed
            if keystroke_intervals and len(keystroke_intervals) > 0:
                avg_interval = sum(keystroke_intervals) / len(keystroke_intervals)
                # Slower typing (higher interval) suggests stress/frustration
                # Faster typing suggests engagement
                speed_score = 1.0 - min(1.0, avg_interval / 0.5)
            else:
                speed_score = 0.5
            
            # Analyze accuracy
            if total_chars > 0:
                error_rate = mistakes / total_chars
                # More errors suggest frustration
                accuracy_score = 1.0 - min(1.0, error_rate)
            else:
                accuracy_score = 0.5
            
            # Weighted combination
            emotion_score = (0.6 * accuracy_score) + (0.4 * speed_score)
            return max(0.0, min(1.0, float(emotion_score)))
            
        except Exception as e:
            logger.debug(f"Typing analysis error: {e}, returning neutral")
            return 0.5
    
    def classify_behavior(self, emotion_score: float) -> str:
        """Classify typing behavior based on emotion score."""
        if emotion_score < 0.3:
            return "frustrated"
        elif emotion_score > 0.7:
            return "engaged"
        else:
            return "neutral"


# Global instance
typing_analyzer = TypingBehaviorAnalyzer()


def analyze_typing(keystroke_intervals=None, mistakes: int = 0, total_chars: int = 0) -> float:
    """Convenience function for typing analysis."""
    try:
        return typing_analyzer.analyze(keystroke_intervals, mistakes, total_chars)
    except Exception:
        return 0.5
