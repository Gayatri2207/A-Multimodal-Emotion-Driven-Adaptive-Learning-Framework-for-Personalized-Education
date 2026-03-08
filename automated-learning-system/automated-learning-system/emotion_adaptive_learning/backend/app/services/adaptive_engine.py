import gym
import numpy as np
from stable_baselines3 import PPO

class AdaptiveEnv(gym.Env):

    def __init__(self):
        super(AdaptiveEnv, self).__init__()
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)

    def reset(self):
        self.state = np.random.rand(2)
        return self.state

    def step(self, action):
        reward = np.random.rand()
        done = True
        return self.state, reward, done, {}

env = AdaptiveEnv()
model = PPO("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=1000)

def get_adaptive_action(emotion_score, performance_score):
    obs = np.array([emotion_score, performance_score])
    action, _ = model.predict(obs)
    actions = ["Decrease Difficulty", "Maintain Level", "Increase Difficulty"]
    return actions[action]
