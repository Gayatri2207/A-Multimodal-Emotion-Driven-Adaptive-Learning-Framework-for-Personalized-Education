import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO


class AdaptiveEnv(gym.Env):

    def __init__(self):
        super().__init__()

        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=1,
            shape=(2,),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.random.rand(2).astype(np.float32)
        return self.state, {}

    def step(self, action):
        reward = float(np.random.rand())
        terminated = True
        truncated = False

        return self.state, reward, terminated, truncated, {}


env = AdaptiveEnv()
model = PPO("MlpPolicy", env, verbose=0)

# ⚡ DO NOT train automatically
# model.learn(total_timesteps=1000)


def train_model():
    model.learn(total_timesteps=1000)


def get_adaptive_action(emotion_score, performance_score):
    obs = np.array([emotion_score, performance_score], dtype=np.float32)
    action, _ = model.predict(obs)
    actions = ["Decrease Difficulty", "Maintain Level", "Increase Difficulty"]
    return actions[action]


# Keep compatibility for routes
adjust_difficulty = get_adaptive_action