"""Reinforcement Learning Engine for adaptive learning actions."""

import os
from app.config import settings
from app.utils.logger import logger

# Try to import heavy ML dependencies, but don't fail if missing
try:
    import numpy as np
    from stable_baselines3 import PPO
    HAS_ML = True
except Exception:
    HAS_ML = False
    logger.warning("ML dependencies not available (torch may have DLL issues), using heuristic fallback")


class RLEngine:
    """RL engine for computing adaptive learning actions."""

    def __init__(self):
        self.model = None
        self.has_model = False
        self._load_model()

    def _load_model(self):
        """Load the RL model if it exists."""
        if not HAS_ML:
            logger.info("RL Engine: ML libs not available, using heuristic mode")
            return

        if os.path.exists(settings.RL_MODEL_PATH):
            try:
                self.model = PPO.load(settings.RL_MODEL_PATH)
                self.has_model = True
                logger.info(f"✓ RL Model loaded from {settings.RL_MODEL_PATH}")
            except Exception as e:
                logger.warning(f"Failed to load RL model: {e}, using heuristic fallback")
                self.has_model = False
        else:
            logger.info(f"RL Model not found at {settings.RL_MODEL_PATH}, using heuristic fallback")

    def get_adaptive_action(
        self,
        emotion_score: float,
        performance_score: float,
        attempts: int = 1,
        time_taken_s: float = 0.0,
    ) -> str:
        """
        Get adaptive learning action based on emotion, performance, attempts, and time.

        Args:
            emotion_score:     0=frustrated/negative, 1=engaged/positive
            performance_score: 0=poor, 1=excellent (fraction of tests passed)
            attempts:          number of submission attempts for current problem
            time_taken_s:      seconds spent on current problem

        Returns:
            One of ['relax', 'hint', 'challenge', 'practice']

        Logic:
            frustrated (emotion<0.30) + low success (<0.40) → relax
            frustrated + medium success → hint
            focused  (0.30–0.70) + low success → hint
            focused  + medium success → practice
            focused  + high success (>0.70) → challenge
            bored/confident (emotion>0.70) + high success → challenge
            too many attempts (>5) → hint
            very fast + high success → challenge (probably too easy)
        """
        try:
            emotion_score     = max(0.0, min(1.0, float(emotion_score)))
            performance_score = max(0.0, min(1.0, float(performance_score)))
            attempts          = max(1, int(attempts))

            # Try RL model prediction first
            if self.has_model and HAS_ML:
                try:
                    import numpy as _np
                    obs = _np.array(
                        [emotion_score, performance_score,
                         min(attempts / 10.0, 1.0), min(time_taken_s / 300.0, 1.0)],
                        dtype=_np.float32,
                    )
                    action_idx, _ = self.model.predict(obs, deterministic=True)
                    action_map = {0: "relax", 1: "hint", 2: "practice", 3: "challenge"}
                    return action_map.get(int(action_idx), "practice")
                except Exception as e:
                    logger.debug(f"RL model prediction failed: {e}, using heuristic")

            # ── Enhanced heuristic ─────────────────────────────────────────
            frustrated = emotion_score < 0.30
            neutral    = 0.30 <= emotion_score <= 0.70
            confident  = emotion_score > 0.70

            low_perf    = performance_score < 0.40
            medium_perf = 0.40 <= performance_score <= 0.70
            high_perf   = performance_score > 0.70

            too_many_attempts = attempts > 5
            quick_solve       = time_taken_s < 60 and high_perf and attempts == 1

            if frustrated and low_perf:
                return "relax"
            if frustrated and (medium_perf or low_perf) and too_many_attempts:
                return "relax"
            if frustrated:
                return "hint"
            if too_many_attempts and (low_perf or medium_perf):
                return "hint"
            if neutral and low_perf:
                return "hint"
            if (confident or quick_solve) and high_perf:
                return "challenge"
            if neutral and high_perf:
                return "challenge"
            if neutral and medium_perf:
                return "practice"
            if confident and medium_perf:
                return "practice"
            return "practice"

        except Exception as e:
            logger.error(f"Error in get_adaptive_action: {e}")
            return "practice"

    def get_recommended_difficulty(
        self,
        emotion_score: float,
        performance_score: float,
        attempts: int = 1,
        time_taken_s: float = 0.0,
    ) -> str:
        """Map adaptive action to a recommended difficulty level."""
        action = self.get_adaptive_action(emotion_score, performance_score, attempts, time_taken_s)
        return {"relax": "easy", "hint": "easy", "practice": "medium", "challenge": "hard"}.get(action, "medium")


# Global instance
rl_engine = RLEngine()
