#!/usr/bin/env python3
"""
Phase 2: Intrinsic Motivation

Implements curiosity-driven exploration and intrinsic motivation mechanisms.

Based on:
- Pathak et al. (2017) "Curiosity-driven Exploration by Self-supervised Prediction"
  Uses prediction error as intrinsic reward for exploration
- Silver et al. (2017) "Mastering the Game of Go without Human Knowledge"
  Self-play learning for continuous improvement

Key Concepts:
- Curiosity: Exploration driven by prediction error (novelty)
- Novelty Detection: Information gain from new experiences
- Self-Play: Learning through self-generated training data
"""

import json
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import hashlib


# ==================== Domain Classes ====================

@dataclass
class MotivationScore:
    """
    Represents an intrinsic motivation score for an exploration area.

    Attributes:
        - area: The exploration area identifier
        - curiosity_score: Novelty based on prediction error (0.0 - 1.0)
        - uncertainty_score: Epistemic uncertainty (0.0 - 1.0)
        - predicted_impact: Expected impact on performance (0.0 - 1.0)
        - total_score: Combined motivation score (0.0 - 1.0)
    """
    area: str
    curiosity_score: float
    uncertainty_score: float
    predicted_impact: float
    total_score: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "area": self.area,
            "curiosity_score": self.curiosity_score,
            "uncertainty_score": self.uncertainty_score,
            "predicted_impact": self.predicted_impact,
            "total_score": self.total_score,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ExplorationEpisode:
    """
    Represents a single exploration episode.

    Attributes:
        - episode_id: Unique identifier
        - area: Exploration area
        - state: Initial state
        - action: Action taken
        - next_state: Resulting state
        - prediction_error: Prediction error (intrinsic reward)
        - timestamp: When episode occurred
    """
    episode_id: str
    area: str
    state: Dict[str, Any]
    action: str
    next_state: Dict[str, Any]
    prediction_error: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "area": self.area,
            "state": self.state,
            "action": self.action,
            "next_state": self.next_state,
            "prediction_error": self.prediction_error,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SelfPlayResult:
    """
    Result of self-play training.

    Attributes:
        - agent: Agent identifier
        - num_episodes: Number of episodes played
        - wins: Number of wins
        - losses: Number of losses
        - draws: Number of draws
        - improvement: Performance improvement
    """
    agent: str
    num_episodes: int
    wins: int
    losses: int
    draws: int
    improvement: float
    timestamp: datetime = field(default_factory=datetime.now)


# ==================== Motivation Calculator ====================

class MotivationCalculator:
    """
    Calculate intrinsic motivation scores for exploration areas.

    Motivation Components:
    - Curiosity: Novelty based on prediction error
    - Uncertainty: Epistemic uncertainty about outcomes
    - Impact: Predicted impact on overall performance
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # History of exploration scores
        self.score_history: Dict[str, List[MotivationScore]] = {}

        # Weights for motivation components
        self.curiosity_weight = 0.4
        self.uncertainty_weight = 0.3
        self.impact_weight = 0.3

    def calculate_motivation(
        self,
        exploration_area: str,
        performance_history: List[Dict[str, Any]]
    ) -> MotivationScore:
        """
        Calculate intrinsic motivation score for an exploration area.

        Args:
            exploration_area: Area to explore
            performance_history: Historical performance data

        Returns:
            MotivationScore with detailed breakdown
        """
        # Calculate curiosity based on prediction error
        curiosity_score = self._calculate_curiosity(exploration_area, performance_history)

        # Calculate uncertainty based on variance in performance
        uncertainty_score = self._calculate_uncertainty(exploration_area, performance_history)

        # Calculate predicted impact
        predicted_impact = self._calculate_impact(exploration_area, performance_history)

        # Combine scores with weights
        total_score = (
            self.curiosity_weight * curiosity_score +
            self.uncertainty_weight * uncertainty_score +
            self.impact_weight * predicted_impact
        )

        score = MotivationScore(
            area=exploration_area,
            curiosity_score=curiosity_score,
            uncertainty_score=uncertainty_score,
            predicted_impact=predicted_impact,
            total_score=total_score
        )

        # Store in history
        if exploration_area not in self.score_history:
            self.score_history[exploration_area] = []
        self.score_history[exploration_area].append(score)

        # Save to storage
        self._save_score(score)

        return score

    def _calculate_curiosity(self, area: str, history: List[Dict[str, Any]]) -> float:
        """
        Calculate curiosity score based on novelty.

        Novel areas have higher curiosity scores.
        """
        if not history:
            return 1.0  # Maximum curiosity for unexplored areas

        # Check if area has been explored recently
        area_explorations = [h for h in history if h.get("area") == area]

        if not area_explorations:
            return 1.0

        # Recent explorations reduce curiosity
        most_recent = max(area_explorations, key=lambda x: x.get("timestamp", ""))
        time_since = (datetime.now() - datetime.fromisoformat(most_recent["timestamp"])).days

        # Curiosity decays over time but never reaches zero
        curiosity = min(1.0, 0.1 + time_since / 30.0)

        return curiosity

    def _calculate_uncertainty(self, area: str, history: List[Dict[str, Any]]) -> float:
        """
        Calculate uncertainty based on performance variance.

        High variance indicates high uncertainty.
        """
        area_history = [h for h in history if h.get("area") == area]

        if len(area_history) < 3:
            return 1.0  # High uncertainty with limited data

        performances = [h.get("performance", 0.5) for h in area_history]

        if not performances:
            return 1.0

        # Calculate variance
        mean = sum(performances) / len(performances)
        variance = sum((p - mean) ** 2 for p in performances) / len(performances)

        # Normalize to 0-1 range
        uncertainty = min(1.0, variance * 2.0)

        return uncertainty

    def _calculate_impact(self, area: str, history: List[Dict[str, Any]]) -> float:
        """
        Calculate predicted impact on overall performance.

        Areas with high potential for improvement get higher scores.
        """
        area_history = [h for h in history if h.get("area") == area]

        if not area_history:
            return 0.5  # Neutral impact for unknown areas

        # Estimate impact based on recent performance trend
        recent = sorted(area_history, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]

        if len(recent) < 2:
            return 0.5

        # Calculate trend
        performances = [h.get("performance", 0.5) for h in recent]
        trend = (performances[0] - performances[-1]) / len(performances)

        # Positive trend indicates potential for improvement
        impact = 0.5 + trend

        return max(0.0, min(1.0, impact))

    def get_top_areas(self, n: int = 5) -> List[str]:
        """
        Get top exploration areas by motivation score.

        Args:
            n: Number of top areas to return

        Returns:
            List of area identifiers
        """
        all_scores = []

        for area, scores in self.score_history.items():
            if scores:
                latest = max(scores, key=lambda x: x.timestamp)
                all_scores.append((area, latest.total_score))

        # Sort by total score
        all_scores.sort(key=lambda x: x[1], reverse=True)

        return [area for area, _ in all_scores[:n]]

    def _save_score(self, score: MotivationScore):
        """Save score to storage."""
        score_file = self.storage_dir / f"motivation_{score.area}.json"
        with open(score_file, 'w', encoding='utf-8') as f:
            json.dump(score.to_dict(), f, indent=2)


# ==================== Curiosity Explorer ====================

class CuriosityExplorer:
    """
    Curiosity-driven exploration using prediction error as intrinsic reward.

    Based on Pathak et al. (2017):
    - Use prediction error of forward dynamics model as intrinsic reward
    - Agent is rewarded for visiting novel states
    - Encourages exploration even without extrinsic rewards
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Exploration history
        self.episodes: List[ExplorationEpisode] = []

        # Prediction model (simplified - in practice would be neural network)
        self.prediction_model: Dict[str, Any] = {}

    def explore_novel_areas(self, candidates: List[str]) -> List[str]:
        """
        Select novel areas to explore based on curiosity.

        Args:
            candidates: List of candidate exploration areas

        Returns:
            List of selected areas sorted by novelty
        """
        # Calculate novelty for each candidate
        novelty_scores = []

        for area in candidates:
            # Count past explorations
            past_explorations = [e for e in self.episodes if e.area == area]

            # Fewer explorations = higher novelty
            exploration_count = len(past_explorations)
            novelty = 1.0 / (1.0 + exploration_count * 0.1)

            novelty_scores.append((area, novelty))

        # Sort by novelty
        novelty_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top candidates
        return [area for area, _ in novelty_scores]

    def compute_prediction_error(
        self,
        state: Dict[str, Any],
        action: str,
        next_state: Dict[str, Any]
    ) -> float:
        """
        Compute prediction error for state transition.

        Prediction error = ||predicted_next_state - actual_next_state||

        Args:
            state: Current state
            action: Action taken
            next_state: Actual next state

        Returns:
            Prediction error (higher = more novel)
        """
        # Create state-action key
        state_key = self._state_to_key(state)
        key = f"{state_key}_{action}"

        # Get predicted next state (simplified)
        if key in self.prediction_model:
            predicted = self.prediction_model[key]
        else:
            # No prediction yet = maximum error
            return 1.0

        # Compute error (simplified Euclidean distance)
        error = self._compute_state_distance(predicted, next_state)

        return error

    def compute_intrinsic_reward(
        self,
        state: Dict[str, Any],
        action: str,
        next_state: Dict[str, Any]
    ) -> float:
        """
        Compute intrinsic reward based on prediction error.

        Intrinsic reward = prediction error (normalized)

        Args:
            state: Current state
            action: Action taken
            next_state: Actual next state

        Returns:
            Intrinsic reward (0.0 - 1.0)
        """
        prediction_error = self.compute_prediction_error(state, action, next_state)

        # Normalize to 0-1 range
        intrinsic_reward = min(1.0, prediction_error)

        return intrinsic_reward

    def update_prediction_model(
        self,
        state: Dict[str, Any],
        action: str,
        next_state: Dict[str, Any]
    ):
        """
        Update prediction model with new experience.

        Args:
            state: Current state
            action: Action taken
            next_state: Actual next state
        """
        state_key = self._state_to_key(state)
        key = f"{state_key}_{action}"

        # Update model (simplified moving average)
        if key in self.prediction_model:
            # Update with moving average
            alpha = 0.1
            old_predicted = self.prediction_model[key]
            new_predicted = self._merge_states(old_predicted, next_state, alpha)
            self.prediction_model[key] = new_predicted
        else:
            # Initialize prediction
            self.prediction_model[key] = next_state.copy()

    def record_episode(
        self,
        area: str,
        state: Dict[str, Any],
        action: str,
        next_state: Dict[str, Any]
    ) -> ExplorationEpisode:
        """
        Record an exploration episode.

        Args:
            area: Exploration area
            state: Current state
            action: Action taken
            next_state: Next state

        Returns:
            Recorded episode
        """
        # Compute prediction error
        prediction_error = self.compute_prediction_error(state, action, next_state)

        # Create episode
        episode_id = hashlib.md5(f"{area}_{action}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        episode = ExplorationEpisode(
            episode_id=episode_id,
            area=area,
            state=state,
            action=action,
            next_state=next_state,
            prediction_error=prediction_error
        )

        # Store episode
        self.episodes.append(episode)

        # Update prediction model
        self.update_prediction_model(state, action, next_state)

        # Save episode
        self._save_episode(episode)

        return episode

    def _state_to_key(self, state: Dict[str, Any]) -> str:
        """Convert state to string key."""
        # Simplified: use sorted items
        items = sorted(state.items())
        return str(items)

    def _compute_state_distance(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> float:
        """Compute distance between two states."""
        # Simplified: count differing keys
        all_keys = set(state1.keys()).union(set(state2.keys()))

        if not all_keys:
            return 0.0

        diff_count = 0
        for key in all_keys:
            val1 = state1.get(key)
            val2 = state2.get(key)
            if val1 != val2:
                diff_count += 1

        return diff_count / len(all_keys)

    def _merge_states(self, state1: Dict[str, Any], state2: Dict[str, Any], alpha: float) -> Dict[str, Any]:
        """Merge two states with weighted average."""
        merged = {}
        all_keys = set(state1.keys()).union(set(state2.keys()))

        for key in all_keys:
            val1 = state1.get(key)
            val2 = state2.get(key)

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                merged[key] = alpha * val2 + (1 - alpha) * val1
            else:
                # For non-numeric values, prefer state2
                merged[key] = val2

        return merged

    def _save_episode(self, episode: ExplorationEpisode):
        """Save episode to storage."""
        episode_file = self.storage_dir / f"episode_{episode.episode_id}.json"
        with open(episode_file, 'w', encoding='utf-8') as f:
            json.dump(episode.to_dict(), f, indent=2)


# ==================== Novelty Detector ====================

class NoveltyDetector:
    """
    Detect novel information and experiences.

    Novelty Metrics:
    - Information Gain: New information compared to knowledge base
    - Surprise: Unexpected outcomes
    - Diversity: Different from existing experiences
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Knowledge base (simplified)
        self.knowledge_base: Dict[str, Any] = {}

        # Novelty history
        self.novelty_history: List[Dict[str, Any]] = []

    def detect_novelty(self, item: Dict[str, Any], knowledge_base: Dict[str, Any]) -> float:
        """
        Detect novelty of an item compared to knowledge base.

        Args:
            item: Item to assess for novelty
            knowledge_base: Existing knowledge base

        Returns:
            Novelty score (0.0 - 1.0)
        """
        if not knowledge_base:
            return 1.0  # Maximum novelty for empty KB

        # Check for similar items
        similarity = self._compute_similarity(item, knowledge_base)

        # Novelty = 1 - similarity
        novelty = 1.0 - similarity

        return novelty

    def compute_information_gain(self, item: Dict[str, Any]) -> float:
        """
        Compute information gain from adding item to knowledge base.

        Args:
            item: Item to add

        Returns:
            Information gain (0.0 - 1.0)
        """
        # Compute entropy reduction (simplified)
        current_keys = set(self.knowledge_base.keys())
        new_keys = set(item.keys())

        # New keys contribute to information gain
        new_information = new_keys - current_keys

        if not current_keys:
            return 1.0

        gain = len(new_information) / len(current_keys.union(new_keys))

        return gain

    def is_surprising(self, item: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """
        Determine if item is surprising (deviates from expectations).

        Args:
            item: Observed item
            expected: Expected item

        Returns:
            True if surprising
        """
        # Compute deviation
        deviation = self._compute_deviation(item, expected)

        # Threshold for surprise
        surprise_threshold = 0.5

        return deviation > surprise_threshold

    def _compute_similarity(self, item: Dict[str, Any], kb: Dict[str, Any]) -> float:
        """Compute similarity between item and knowledge base."""
        # Count matching keys
        item_keys = set(item.keys())
        kb_keys = set(kb.keys())

        if not item_keys:
            return 0.0

        intersection = item_keys.intersection(kb_keys)
        similarity = len(intersection) / len(item_keys)

        return similarity

    def _compute_deviation(self, item: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """Compute deviation from expected."""
        all_keys = set(item.keys()).union(set(expected.keys()))

        if not all_keys:
            return 0.0

        deviation_count = 0
        for key in all_keys:
            item_val = item.get(key)
            expected_val = expected.get(key)
            if item_val != expected_val:
                deviation_count += 1

        return deviation_count / len(all_keys)


# ==================== Self-Play Learner ====================

class SelfPlayLearner:
    """
    Self-play learning for continuous improvement.

    Based on Silver et al. (2017):
    - Agent learns by playing against itself
    - Generates training data through self-play
    - Continuously improves through iterative training
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Self-play history
        self.training_history: List[SelfPlayResult] = []

        # Agent versions (checkpointing)
        self.agent_versions: Dict[str, int] = {}

    def self_play_training(self, agent: str, num_episodes: int = 100) -> SelfPlayResult:
        """
        Train agent through self-play.

        Args:
            agent: Agent identifier
            num_episodes: Number of episodes to play

        Returns:
            Training result
        """
        wins = 0
        losses = 0
        draws = 0

        # Simulate self-play episodes
        for episode in range(num_episodes):
            # Generate opponent (current or previous version)
            opponent = self.generate_opponent(agent)

            # Simulate episode (simplified)
            result = self._simulate_episode(agent, opponent)

            if result == "win":
                wins += 1
            elif result == "loss":
                losses += 1
            else:
                draws += 1

        # Calculate improvement
        improvement = self._calculate_improvement(agent, wins, losses, num_episodes)

        # Create result
        result = SelfPlayResult(
            agent=agent,
            num_episodes=num_episodes,
            wins=wins,
            losses=losses,
            draws=draws,
            improvement=improvement
        )

        # Update agent version
        self.agent_versions[agent] = self.agent_versions.get(agent, 0) + 1

        # Store result
        self.training_history.append(result)
        self._save_result(result)

        return result

    def generate_opponent(self, agent: str) -> str:
        """
        Generate opponent for self-play.

        Can be current version or previous version.

        Args:
            agent: Agent identifier

        Returns:
            Opponent identifier
        """
        # Get current version
        current_version = self.agent_versions.get(agent, 0)

        # With probability, use previous version
        if current_version > 0 and random.random() < 0.3:
            # Use previous version
            return f"{agent}_v{current_version - 1}"

        # Use current version (play against self)
        return agent

    def evaluate_self_play(self, agent: str) -> Dict[str, Any]:
        """
        Evaluate agent through self-play evaluation.

        Args:
            agent: Agent identifier

        Returns:
            Evaluation metrics
        """
        # Get recent training results
        agent_history = [r for r in self.training_history if r.agent == agent]

        if not agent_history:
            return {
                "agent": agent,
                "total_episodes": 0,
                "win_rate": 0.0,
                "improvement": 0.0
            }

        # Aggregate statistics
        total_episodes = sum(r.num_episodes for r in agent_history)
        total_wins = sum(r.wins for r in agent_history)
        total_losses = sum(r.losses for r in agent_history)

        win_rate = total_wins / total_episodes if total_episodes > 0 else 0.0

        # Average improvement
        avg_improvement = sum(r.improvement for r in agent_history) / len(agent_history)

        return {
            "agent": agent,
            "total_episodes": total_episodes,
            "wins": total_wins,
            "losses": total_losses,
            "win_rate": win_rate,
            "improvement": avg_improvement
        }

    def _simulate_episode(self, agent: str, opponent: str) -> str:
        """
        Simulate a single self-play episode.

        Args:
            agent: Agent identifier
            opponent: Opponent identifier

        Returns:
            Result: "win", "loss", or "draw"
        """
        # Simplified: random outcome with bias toward newer versions
        agent_version = self.agent_versions.get(agent, 0)
        opponent_version = self.agent_versions.get(opponent.replace("_v" + opponent.split("_v")[-1] if "_v" in opponent else ""), 0)

        # Newer versions have advantage
        version_diff = agent_version - opponent_version

        # Probability of winning
        win_prob = 0.5 + version_diff * 0.1

        # Determine outcome
        rand = random.random()
        if rand < win_prob:
            return "win"
        elif rand < win_prob + (1.0 - win_prob) / 2:
            return "loss"
        else:
            return "draw"

    def _calculate_improvement(self, agent: str, wins: int, losses: int, total: int) -> float:
        """Calculate improvement score."""
        if total == 0:
            return 0.0

        # Win rate
        win_rate = wins / total

        # Get previous win rate
        agent_history = [r for r in self.training_history if r.agent == agent]

        if agent_history:
            prev_wins = sum(r.wins for r in agent_history)
            prev_total = sum(r.num_episodes for r in agent_history)
            prev_win_rate = prev_wins / prev_total if prev_total > 0 else 0.0
        else:
            prev_win_rate = 0.5  # Baseline

        # Improvement = change in win rate
        improvement = win_rate - prev_win_rate

        return improvement

    def _save_result(self, result: SelfPlayResult):
        """Save result to storage."""
        result_file = self.storage_dir / f"selfplay_{result.agent}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "agent": result.agent,
                "num_episodes": result.num_episodes,
                "wins": result.wins,
                "losses": result.losses,
                "draws": result.draws,
                "improvement": result.improvement,
                "timestamp": result.timestamp.isoformat()
            }, f, indent=2)


# ==================== Main ====================

def main():
    """Simple demo of Intrinsic Motivation components."""
    print("=" * 70)
    print("🎯 Intrinsic Motivation - Demo")
    print("=" * 70)
    print()

    # Motivation Calculator
    print("📊 Motivation Calculator...")
    calculator = MotivationCalculator()

    score = calculator.calculate_motivation(
        exploration_area="code_refactoring",
        performance_history=[
            {"area": "code_refactoring", "performance": 0.7, "timestamp": "2026-03-10T10:00:00"}
        ]
    )
    print(f"  Curiosity: {score.curiosity_score:.2f}")
    print(f"  Uncertainty: {score.uncertainty_score:.2f}")
    print(f"  Impact: {score.predicted_impact:.2f}")
    print(f"  Total: {score.total_score:.2f}")

    # Curiosity Explorer
    print("\n🔍 Curiosity Explorer...")
    explorer = CuriosityExplorer()

    novel_areas = explorer.explore_novel_areas(["area_a", "area_b", "area_c"])
    print(f"  Novel areas: {novel_areas}")

    # Self-Play Learner
    print("\n🎮 Self-Play Learner...")
    learner = SelfPlayLearner()

    result = learner.self_play_training("agent_1", num_episodes=10)
    print(f"  Wins: {result.wins}, Losses: {result.losses}, Draws: {result.draws}")
    print(f"  Improvement: {result.improvement:.2f}")

    print("\n" + "=" * 70)
    print("✅ Intrinsic Motivation demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
