import gymnasium as gym
import numpy as np
import os
from stable_baselines3 import PPO


class AdaptiveEnv(gym.Env):
    """
    RL environment for adaptive learning difficulty adjustment.

    Observation: [emotion_score (0-1), performance_score (0-1),
                  attempts_norm (0-1), time_norm (0-1)]
    Actions:
        0 → relax       (reduce stress)
        1 → hint        (provide guidance)
        2 → challenge   (increase difficulty)
        3 → practice    (normal progression)
    """

    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(4)
        # 4-dimensional observation: emotion, performance, attempts_norm, time_norm
        self.observation_space = gym.spaces.Box(
            low=np.float32([0.0, 0.0, 0.0, 0.0]),
            high=np.float32([1.0, 1.0, 1.0, 1.0]),
            dtype=np.float32,
        )
        self.state = np.array([0.5, 0.5, 0.1, 0.1], dtype=np.float32)
        self._step_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = self.np_random.uniform(low=0.0, high=1.0, size=(4,)).astype(np.float32)
        self._step_count = 0
        return self.state, {}

    def step(self, action):
        emotion, perf = float(self.state[0]), float(self.state[1])
        self._step_count += 1

        # Reward shaping based on action appropriateness
        if action == 0:   # relax
            reward = 1.0 if emotion < 0.35 else -0.5
        elif action == 1:  # hint
            reward = 1.0 if emotion < 0.5 and perf < 0.45 else -0.3
        elif action == 2:  # challenge
            reward = 1.0 if perf > 0.65 and emotion > 0.55 else -0.4
        else:              # practice
            reward = 0.5   # always somewhat valid

        # Simulate state transition after action
        delta_e = float(self.np_random.uniform(-0.1, 0.1))
        delta_p = float(self.np_random.uniform(-0.05, 0.1))
        new_emotion = np.clip(emotion + delta_e, 0.0, 1.0)
        new_perf = np.clip(perf + delta_p, 0.0, 1.0)
        # Increment normalised attempts and time
        new_attempts = np.clip(float(self.state[2]) + 0.05, 0.0, 1.0)
        new_time     = np.clip(float(self.state[3]) + 0.03, 0.0, 1.0)
        self.state = np.array([new_emotion, new_perf, new_attempts, new_time], dtype=np.float32)

        terminated = self._step_count >= 50
        return self.state, reward, terminated, False, {}


def train_model(timesteps: int = 50_000, save_path: str = "../backend/models/ppo_model.zip"):
    """Train the PPO agent and save the model."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    env = AdaptiveEnv()
    model = PPO("MlpPolicy", env, verbose=1, n_steps=256, batch_size=64, n_epochs=10)
    model.learn(total_timesteps=timesteps)
    model.save(save_path)
    print(f"✓ PPO model saved to {save_path}")
    return model


def get_adaptive_action(emotion_score: float, performance_score: float) -> str:
    """Heuristic fallback — mirrors rl_engine.py for compatibility."""
    actions = {0: "relax", 1: "hint", 2: "challenge", 3: "practice"}
    if emotion_score < 0.3:
        return actions[0]
    if emotion_score < 0.5 and performance_score < 0.4:
        return actions[1]
    if performance_score > 0.7 and emotion_score > 0.6:
        return actions[2]
    return actions[3]


# Keep route compatibility alias
adjust_difficulty = get_adaptive_action


if __name__ == "__main__":
    train_model()
