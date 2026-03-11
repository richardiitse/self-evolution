#!/usr/bin/env python3
"""
Phase 2: Intrinsic Motivation Strategies

Intrinsic motivation capabilities for the self-evolution agent.

Based on:
- Pathak et al. (2017) "Curiosity-driven Exploration by Self-supervised Prediction"
- Silver et al. (2017) "Mastering the Game of Go without Human Knowledge"

Components:
- Motivation Calculator: Calculate intrinsic motivation scores
- Curiosity Explorer: Explore novel areas using prediction error
- Novelty Detector: Detect novel information
- Self-Play Learner: Self-play training for improvement
- Opportunity Detector: Detect improvement opportunities
- Score Calculator: Score opportunities by impact/effort
- Priority Ranker: Rank opportunities by priority
- Pattern Extractor: Extract patterns from data
- Pattern Analyzer: Analyze patterns for insights
- Pattern Matcher: Match patterns against data
"""

from .intrinsic_motivation import (
    MotivationScore,
    MotivationCalculator,
    CuriosityExplorer,
    NoveltyDetector,
    SelfPlayLearner
)

from .opportunity_scoring import (
    Opportunity,
    OpportunityDetector,
    ScoreCalculator,
    PriorityRanker
)

from .pattern_recognition import (
    Pattern,
    PatternExtractor,
    PatternAnalyzer,
    PatternMatcher
)

__all__ = [
    # Intrinsic Motivation
    "MotivationScore",
    "MotivationCalculator",
    "CuriosityExplorer",
    "NoveltyDetector",
    "SelfPlayLearner",
    # Opportunity Scoring
    "Opportunity",
    "OpportunityDetector",
    "ScoreCalculator",
    "PriorityRanker",
    # Pattern Recognition
    "Pattern",
    "PatternExtractor",
    "PatternAnalyzer",
    "PatternMatcher"
]

__version__ = "1.0.0"
