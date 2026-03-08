"""Tests for multimodal fusion and RL engine."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.multimodal.fusion import weighted_fusion
from app.services.rl_engine import RLEngine


class TestWeightedFusion:
    def test_all_signals(self):
        score = weighted_fusion(0.8, 0.6, 0.4)
        assert 0.0 <= score <= 1.0
        # Expected: 0.8*0.5 + 0.6*0.3 + 0.4*0.2 = 0.4+0.18+0.08 = 0.66
        assert abs(score - 0.66) < 1e-6

    def test_facial_only(self):
        score = weighted_fusion(0.9, None, None)
        assert abs(score - 0.9) < 1e-6

    def test_no_signals(self):
        score = weighted_fusion(None, None, None)
        assert score == 0.5

    def test_out_of_range_clamped(self):
        score = weighted_fusion(1.5, -0.5, 0.5)
        assert 0.0 <= score <= 1.0

    def test_two_signals(self):
        score = weighted_fusion(0.8, 0.4, None)
        # weights renormalized: facial 0.5, speech 0.3 → 0.8*0.625 + 0.4*0.375
        assert 0.0 <= score <= 1.0


class TestRLEngine:
    def setup_method(self):
        self.engine = RLEngine()

    def test_stress_gives_relax(self):
        action = self.engine.get_adaptive_action(0.1, 0.5)
        assert action == "relax"

    def test_struggling_gives_hint(self):
        action = self.engine.get_adaptive_action(0.4, 0.3)
        assert action == "hint"

    def test_confident_gives_challenge(self):
        action = self.engine.get_adaptive_action(0.8, 0.9)
        assert action == "challenge"

    def test_normal_gives_practice(self):
        action = self.engine.get_adaptive_action(0.6, 0.6)
        assert action == "practice"

    def test_returns_string(self):
        result = self.engine.get_adaptive_action(0.5, 0.5)
        assert isinstance(result, str)
        assert result in {"relax", "hint", "challenge", "practice"}

    def test_boundary_values(self):
        assert self.engine.get_adaptive_action(0.0, 0.0) == "relax"
        assert self.engine.get_adaptive_action(1.0, 1.0) == "challenge"
