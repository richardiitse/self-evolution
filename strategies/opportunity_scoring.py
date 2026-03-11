#!/usr/bin/env python3
"""
Phase 2: Opportunity Scoring

Detects and scores improvement opportunities based on performance analysis.

Key Concepts:
- Weakness Detection: Identify areas needing improvement
- Impact Estimation: Predict impact of improvements
- Effort Estimation: Estimate required effort
- Priority Ranking: Rank by impact/effort ratio
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import hashlib


# ==================== Domain Classes ====================

@dataclass
class Opportunity:
    """
    Represents an improvement opportunity.

    Attributes:
        - opportunity_id: Unique identifier
        - description: Description of opportunity
        - impact_score: Expected impact (0.0 - 1.0)
        - effort_score: Required effort (0.0 - 1.0, higher = more effort)
        - risk_score: Associated risk (0.0 - 1.0)
        - novelty_score: How novel the solution is (0.0 - 1.0)
        - total_score: Combined priority score (0.0 - 1.0)
        - category: Opportunity category
        - status: Current status
    """
    opportunity_id: str
    description: str
    impact_score: float
    effort_score: float
    risk_score: float
    novelty_score: float
    total_score: float
    category: str = "general"
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "description": self.description,
            "impact_score": self.impact_score,
            "effort_score": self.effort_score,
            "risk_score": self.risk_score,
            "novelty_score": self.novelty_score,
            "total_score": self.total_score,
            "category": self.category,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Weakness:
    """
    Represents a detected weakness.

    Attributes:
        - weakness_id: Unique identifier
        - area: Area where weakness exists
        - severity: Severity level (0.0 - 1.0)
        - frequency: How often it occurs
        - description: Description of weakness
    """
    weakness_id: str
    area: str
    severity: float
    frequency: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weakness_id": self.weakness_id,
            "area": self.area,
            "severity": self.severity,
            "frequency": self.frequency,
            "description": self.description
        }


# ==================== Opportunity Detector ====================

class OpportunityDetector:
    """
    Detect improvement opportunities from performance data.

    Detection Methods:
    - Performance Analysis: Find underperforming areas
    - Weakness Detection: Identify recurring issues
    - Trend Analysis: Find declining performance
    - Gap Analysis: Compare against benchmarks
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Detection history
        self.detected_opportunities: List[Opportunity] = []
        self.detected_weaknesses: List[Weakness] = []

        # Thresholds
        self.performance_threshold = 0.7  # Below this = opportunity
        self.severity_threshold = 0.5

    def detect_opportunities(
        self,
        performance_metrics: Dict[str, float],
        codebase_analyzer: Optional[Any] = None
    ) -> List[Opportunity]:
        """
        Detect improvement opportunities from performance metrics.

        Args:
            performance_metrics: Dictionary of area -> performance score
            codebase_analyzer: Optional codebase analyzer

        Returns:
            List of detected opportunities
        """
        opportunities = []

        # Find underperforming areas
        for area, performance in performance_metrics.items():
            if performance < self.performance_threshold:
                # Create opportunity
                opp_id = self._generate_id(f"opp_{area}")

                # Impact = gap from threshold
                impact = self.performance_threshold - performance

                # Effort estimation (simplified)
                effort = self._estimate_effort(area, performance)

                # Risk estimation
                risk = self._estimate_risk(area, performance)

                # Novelty (simplified)
                novelty = 0.5  # Default

                # Calculate total score
                total = self._calculate_total_score(impact, effort, risk, novelty)

                opportunity = Opportunity(
                    opportunity_id=opp_id,
                    description=f"Improve {area} performance",
                    impact_score=impact,
                    effort_score=effort,
                    risk_score=risk,
                    novelty_score=novelty,
                    total_score=total,
                    category=area,
                    metadata={"current_performance": performance}
                )

                opportunities.append(opportunity)

        # Store opportunities
        self.detected_opportunities.extend(opportunities)

        # Save to storage
        for opp in opportunities:
            self._save_opportunity(opp)

        return opportunities

    def detect_weaknesses(self, observations: List[Dict[str, Any]]) -> List[Opportunity]:
        """
        Detect weaknesses from observations.

        Args:
            observations: List of observations with "area" and "issue" fields

        Returns:
            List of opportunities for fixing weaknesses
        """
        opportunities = []

        # Group observations by area
        area_issues: Dict[str, List[Dict[str, Any]]] = {}

        for obs in observations:
            area = obs.get("area", "unknown")
            if area not in area_issues:
                area_issues[area] = []
            area_issues[area].append(obs)

        # Create opportunities for each area
        for area, issues in area_issues.items():
            if len(issues) < self.severity_threshold * 10:  # Threshold for frequency
                continue

            # Calculate severity based on issue count and types
            severity = min(1.0, len(issues) / 20.0)

            # Create weakness
            weakness_id = self._generate_id(f"weakness_{area}")
            weakness = Weakness(
                weakness_id=weakness_id,
                area=area,
                severity=severity,
                frequency=len(issues),
                description=f"Recurring issues in {area}"
            )

            self.detected_weaknesses.append(weakness)

            # Create opportunity
            opp_id = self._generate_id(f"opp_weakness_{area}")

            # High severity weaknesses have high impact
            impact = severity
            effort = self._estimate_effort(area, 0.5)  # Assume low performance
            risk = severity * 0.8  # Risk correlates with severity
            novelty = 0.3  # Fixing weaknesses is usually not novel

            total = self._calculate_total_score(impact, effort, risk, novelty)

            opportunity = Opportunity(
                opportunity_id=opp_id,
                description=f"Fix recurring issues in {area}",
                impact_score=impact,
                effort_score=effort,
                risk_score=risk,
                novelty_score=novelty,
                total_score=total,
                category="weakness_fix",
                metadata={"weakness_id": weakness_id, "issue_count": len(issues)}
            )

            opportunities.append(opportunity)

            # Save opportunity
            self._save_opportunity(opportunity)

        return opportunities

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{prefix}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]

    def _estimate_effort(self, area: str, performance: float) -> float:
        """Estimate effort required (0.0 = easy, 1.0 = hard)."""
        # Lower performance = more effort needed
        base_effort = 1.0 - performance

        # Adjust by area complexity
        complexity_multipliers = {
            "architecture": 1.2,
            "algorithm": 1.1,
            "optimization": 1.0,
            "bug_fix": 0.8,
            "refactoring": 0.9
        }

        multiplier = complexity_multipliers.get(area, 1.0)
        effort = min(1.0, base_effort * multiplier)

        return effort

    def _estimate_risk(self, area: str, performance: float) -> float:
        """Estimate risk level (0.0 = low, 1.0 = high)."""
        # Core areas have higher risk
        high_risk_areas = {"architecture", "core_algorithm", "data_structures"}

        if area in high_risk_areas:
            return 0.7
        elif performance < 0.3:
            # Very low performance = higher risk
            return 0.6
        else:
            return 0.3

    def _calculate_total_score(
        self,
        impact: float,
        effort: float,
        risk: float,
        novelty: float
    ) -> float:
        """
        Calculate total priority score.

        Higher impact and novelty increase score.
        Higher effort and risk decrease score.
        """
        # Impact-Effort Ratio (like RICE score)
        ie_ratio = impact / (effort + 0.1)  # Avoid division by zero

        # Adjust for risk (higher risk = lower score)
        risk_adjusted = ie_ratio * (1.0 - risk * 0.5)

        # Add novelty bonus
        novelty_bonus = novelty * 0.2

        total = min(1.0, risk_adjusted + novelty_bonus)

        return total

    def _save_opportunity(self, opportunity: Opportunity):
        """Save opportunity to storage."""
        opp_file = self.storage_dir / f"opportunity_{opportunity.opportunity_id}.json"
        with open(opp_file, 'w', encoding='utf-8') as f:
            json.dump(opportunity.to_dict(), f, indent=2)


# ==================== Score Calculator ====================

class ScoreCalculator:
    """
    Calculate scores for opportunities.

    Scoring Dimensions:
    - Impact: Expected benefit
    - Effort: Required work
    - Risk: Potential downside
    - Novelty: Innovation level
    - Urgency: Time sensitivity
    """

    def __init__(self):
        # Weights for different dimensions
        self.impact_weight = 0.35
        self.effort_weight = 0.25
        self.risk_weight = 0.20
        self.novelty_weight = 0.10
        self.urgency_weight = 0.10

    def score_opportunities(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """
        Calculate and update scores for opportunities.

        Args:
            opportunities: List of opportunities to score

        Returns:
            Updated opportunities with scores
        """
        scored_opportunities = []

        for opp in opportunities:
            # Use existing scores if available, otherwise calculate
            if opp.total_score > 0:
                scored = opp
            else:
                # Calculate scores
                impact = self._calculate_impact(opp)
                effort = self._calculate_effort(opp)
                risk = self._calculate_risk(opp)
                novelty = self._calculate_novelty(opp)
                urgency = self._calculate_urgency(opp)

                # Calculate total score
                total = (
                    self.impact_weight * impact +
                    self.effort_weight * (1.0 - effort) +  # Invert effort (lower is better)
                    self.risk_weight * (1.0 - risk) +  # Invert risk (lower is better)
                    self.novelty_weight * novelty +
                    self.urgency_weight * urgency
                )

                # Create updated opportunity
                scored = Opportunity(
                    opportunity_id=opp.opportunity_id,
                    description=opp.description,
                    impact_score=impact,
                    effort_score=effort,
                    risk_score=risk,
                    novelty_score=novelty,
                    total_score=total,
                    category=opp.category,
                    status=opp.status,
                    metadata=opp.metadata,
                    created_at=opp.created_at
                )

            scored_opportunities.append(scored)

        return scored_opportunities

    def _calculate_impact(self, opp: Opportunity) -> float:
        """Calculate impact score."""
        # Use metadata if available
        current_perf = opp.metadata.get("current_performance", 0.5)

        # Impact = gap from optimal (1.0)
        impact = 1.0 - current_perf

        return max(0.0, min(1.0, impact))

    def _calculate_effort(self, opp: Opportunity) -> float:
        """Calculate effort score."""
        # Use category-based estimation
        effort_estimates = {
            "architecture": 0.8,
            "algorithm": 0.7,
            "optimization": 0.6,
            "bug_fix": 0.4,
            "refactoring": 0.5,
            "documentation": 0.3,
            "testing": 0.4
        }

        return effort_estimates.get(opp.category, 0.5)

    def _calculate_risk(self, opp: Opportunity) -> float:
        """Calculate risk score."""
        # Category-based risk
        risk_levels = {
            "architecture": 0.7,
            "core_algorithm": 0.8,
            "optimization": 0.5,
            "bug_fix": 0.3,
            "refactoring": 0.4,
            "weakness_fix": 0.6
        }

        return risk_levels.get(opp.category, 0.4)

    def _calculate_novelty(self, opp: Opportunity) -> float:
        """Calculate novelty score."""
        # Use metadata or estimate from category
        return opp.metadata.get("novelty", 0.5)

    def _calculate_urgency(self, opp: Opportunity) -> float:
        """Calculate urgency score."""
        # Based on severity and frequency
        severity = opp.metadata.get("severity", 0.5)
        frequency = opp.metadata.get("issue_count", 0)

        # More frequent issues = more urgent
        urgency = severity + min(0.5, frequency / 20.0)

        return min(1.0, urgency)


# ==================== Priority Ranker ====================

class PriorityRanker:
    """
    Rank opportunities by priority.

    Ranking Methods:
    - Total Score: Combined impact/effort/risk/novelty
    - Impact-Only: Highest impact first
    - Quick Wins: High impact, low effort
    - Strategic: High novelty, high impact
    """

    def __init__(self):
        self.ranking_method = "total_score"

    def rank_opportunities(
        self,
        opportunities: List[Opportunity],
        method: str = "total_score"
    ) -> List[Opportunity]:
        """
        Rank opportunities by specified method.

        Args:
            opportunities: List of opportunities to rank
            method: Ranking method ("total_score", "impact", "quick_wins", "strategic")

        Returns:
            Sorted list of opportunities
        """
        self.ranking_method = method

        if method == "total_score":
            return self._rank_by_total_score(opportunities)
        elif method == "impact":
            return self._rank_by_impact(opportunities)
        elif method == "quick_wins":
            return self._rank_by_quick_wins(opportunities)
        elif method == "strategic":
            return self._rank_by_strategic(opportunities)
        else:
            return opportunities

    def _rank_by_total_score(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by total score (highest first)."""
        return sorted(opportunities, key=lambda x: x.total_score, reverse=True)

    def _rank_by_impact(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by impact only (highest first)."""
        return sorted(opportunities, key=lambda x: x.impact_score, reverse=True)

    def _rank_by_quick_wins(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by impact/effort ratio (quick wins first)."""
        scored = []
        for opp in opportunities:
            # Calculate quick win score
            ratio = opp.impact_score / (opp.effort_score + 0.1)
            scored.append((opp, ratio))

        # Sort by ratio
        scored.sort(key=lambda x: x[1], reverse=True)

        return [opp for opp, _ in scored]

    def _rank_by_strategic(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by strategic value (high novelty + high impact)."""
        scored = []
        for opp in opportunities:
            # Strategic score = novelty * impact
            strategic = opp.novelty_score * opp.impact_score
            scored.append((opp, strategic))

        # Sort by strategic score
        scored.sort(key=lambda x: x[1], reverse=True)

        return [opp for opp, _ in scored]

    def get_top_n(self, opportunities: List[Opportunity], n: int = 5) -> List[Opportunity]:
        """
        Get top N opportunities.

        Args:
            opportunities: List of opportunities
            n: Number to return

        Returns:
            Top N opportunities
        """
        ranked = self.rank_opportunities(opportunities, self.ranking_method)
        return ranked[:n]


# ==================== Main ====================

def main():
    """Simple demo of Opportunity Scoring components."""
    print("=" * 70)
    print("🎯 Opportunity Scoring - Demo")
    print("=" * 70)
    print()

    # Opportunity Detector
    print("🔍 Detecting opportunities...")
    detector = OpportunityDetector()

    metrics = {
        "algorithm": 0.6,
        "optimization": 0.5,
        "documentation": 0.4
    }

    opportunities = detector.detect_opportunities(metrics)
    print(f"  Found {len(opportunities)} opportunities")
    for opp in opportunities:
        print(f"    - {opp.description}: {opp.total_score:.2f}")

    # Score Calculator
    print("\n📊 Scoring opportunities...")
    calculator = ScoreCalculator()
    scored = calculator.score_opportunities(opportunities)
    for opp in scored:
        print(f"    - {opp.description}: impact={opp.impact_score:.2f}, effort={opp.effort_score:.2f}")

    # Priority Ranker
    print("\n🏆 Ranking opportunities...")
    ranker = PriorityRanker()

    print("  By Total Score:")
    ranked_total = ranker.rank_opportunities(scored, method="total_score")
    for i, opp in enumerate(ranked_total, 1):
        print(f"    {i}. {opp.description}: {opp.total_score:.2f}")

    print("\n  Quick Wins:")
    ranked_quick = ranker.rank_opportunities(scored, method="quick_wins")
    for i, opp in enumerate(ranked_quick, 1):
        print(f"    {i}. {opp.description}")

    print("\n" + "=" * 70)
    print("✅ Opportunity Scoring demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
