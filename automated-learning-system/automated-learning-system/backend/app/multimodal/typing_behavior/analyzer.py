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
