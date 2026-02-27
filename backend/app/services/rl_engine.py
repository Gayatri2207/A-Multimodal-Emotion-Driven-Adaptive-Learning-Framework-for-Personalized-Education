import os
from typing import Tuple
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from ..config import settings
from ..utils.logger import logger

try:
    from stable_baselines3 import PPO
except Exception:
    PPO = None


ACTION_MAP = {0: "relax", 1: "hint", 2: "challenge"}


class EmotionEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)
        self._state = np.zeros(2, dtype=np.float32)

    def step(self, action):
        reward = 0.0
        done = True
        info = {}
        return self._state, reward, done, False, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._state = np.zeros(2, dtype=np.float32)
        return self._state, {}

    def render(self):
        pass


class RLEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.RL_MODEL_PATH
        self.model = None
        if PPO and os.path.exists(self.model_path):
            try:
                self.model = PPO.load(self.model_path)
                logger.info("Loaded RL model from %s" % self.model_path)
            except Exception as e:
                logger.error(f"Failed to load RL model: {e}")

    def get_adaptive_action(self, emotion_score: float, performance_score: float) -> str:
        obs = np.array([emotion_score, performance_score], dtype=np.float32)
        if self.model:
            try:
                action, _ = self.model.predict(obs, deterministic=True)
                return ACTION_MAP.get(int(action), "relax")
            except Exception as e:
                logger.error(f"RL model predict error: {e}")
        # deterministic heuristic fallback
        if emotion_score < 0.4:
            return "relax"
        if performance_score < 0.5:
            return "hint"
        return "challenge"


rl_engine = RLEngine()
