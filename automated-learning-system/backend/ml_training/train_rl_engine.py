"""
RL Adaptive Engine Training Script
===================================
Trains a PPO agent to recommend learning actions (relax / hint / practice / challenge)
based on emotion_score and performance_score inputs.

The reward function teaches the agent:
  - Give 'relax' when emotion is low (stressed student)
  - Give 'hint'  when emotion is mid-low AND performance is low
  - Give 'challenge' when both scores are high (confident student)
  - Give 'practice' in all other cases

Usage:
    cd backend
    .venv\\Scripts\\python ml_training/train_rl_engine.py

Output:
    ./models/ppo_model.zip   (loaded automatically by RLEngine at startup)
"""

import os
import sys
import numpy as np

# ---------------------------------------------------------------------------
# Ensure backend/ is on the Python path when running directly
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import gymnasium as gym
    from gymnasium import spaces
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_checker import check_env
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Install with: pip install gymnasium stable-baselines3")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Custom Gym environment
# ---------------------------------------------------------------------------

class AdaptiveLearningEnv(gym.Env):
    """
    A simple 2-D continuous observation environment.

    Observation: [emotion_score, performance_score]  — both in [0, 1]
    Action:      discrete {0: relax, 1: hint, 2: practice, 3: challenge}
    """

    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
        )
        self.action_space = spaces.Discrete(4)
        self._state = None
        self._step_count = 0
        self._max_steps = 50

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Random starting point in the state space
        self._state = self.np_random.uniform(0.0, 1.0, size=(2,)).astype(np.float32)
        self._step_count = 0
        return self._state, {}

    def step(self, action):
        emotion, perf = float(self._state[0]), float(self._state[1])
        reward = self._compute_reward(action, emotion, perf)

        # Simulate state change based on action
        self._state = self._next_state(action, emotion, perf)
        self._step_count += 1
        terminated = self._step_count >= self._max_steps
        return self._state, reward, terminated, False, {}

    def _compute_reward(self, action: int, emotion: float, perf: float) -> float:
        """
        Reward the agent for choosing the action that matches the student's needs.

        Optimal policy:
          emotion < 0.30                        → relax (0)
          emotion < 0.50 and perf < 0.40        → hint  (1)
          perf > 0.70 and emotion > 0.60        → challenge (3)
          otherwise                             → practice (2)
        """
        if emotion < 0.30:
            optimal = 0  # relax
        elif emotion < 0.50 and perf < 0.40:
            optimal = 1  # hint
        elif perf > 0.70 and emotion > 0.60:
            optimal = 3  # challenge
        else:
            optimal = 2  # practice

        if action == optimal:
            return 1.0
        # Partial reward for close choices
        diff = abs(action - optimal)
        return max(0.0, 1.0 - diff * 0.4)

    def _next_state(self, action: int, emotion: float, perf: float) -> np.ndarray:
        """Simulate how a student's state evolves after an action."""
        # 'relax' improves emotion; 'challenge' can improve performance if mood is good
        delta_e = {0: +0.05, 1: +0.02, 2: 0.0, 3: -0.03}.get(action, 0.0)
        delta_p = {0: -0.02, 1: +0.03, 2: +0.04, 3: +0.06}.get(action, 0.0)
        # Add small noise
        noise = self.np_random.normal(0, 0.02, size=(2,))
        new_e = float(np.clip(emotion + delta_e + noise[0], 0.0, 1.0))
        new_p = float(np.clip(perf + delta_p + noise[1], 0.0, 1.0))
        return np.array([new_e, new_p], dtype=np.float32)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(total_timesteps: int = 100_000, save_path: str = "./models/ppo_model.zip"):
    print("=" * 60)
    print("  EmotiCode — RL Adaptive Engine Training")
    print("=" * 60)

    env = AdaptiveLearningEnv()
    check_env(env, warn=True)

    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,    # encourage exploration
        tensorboard_log=None,
    )

    print(f"\nTraining for {total_timesteps:,} timesteps …")
    model.learn(total_timesteps=total_timesteps, progress_bar=True)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    model.save(save_path)
    print(f"\n✓ Model saved to: {save_path}")

    # Quick evaluation
    print("\n── Quick evaluation (100 episodes) ──")
    obs, _ = env.reset()
    correct = 0
    total = 100
    for _ in range(total):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _, _ = env.step(action)
        if reward >= 1.0:
            correct += 1
        if done:
            obs, _ = env.reset()
    print(f"Optimal action rate: {correct}/{total} ({correct}%)")
    print("\nDone! The RLEngine will load this model automatically on next startup.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train the RL adaptive engine")
    parser.add_argument("--timesteps", type=int, default=100_000, help="Training timesteps")
    parser.add_argument("--save", type=str, default="./models/ppo_model.zip", help="Output path")
    args = parser.parse_args()
    train(total_timesteps=args.timesteps, save_path=args.save)
