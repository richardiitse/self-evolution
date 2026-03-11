#!/usr/bin/env python3
"""
Phase 4: Meta-Learning

Meta-learning capabilities for the self-evolution agent.

Components:
- Meta-Learning Engine: Orchestrates meta-learning across tasks
- Model Architecture Search: Automatic architecture discovery
- Hyperparameter Optimization: Automatic hyperparameter tuning
- Learning Rate Adaptation: Dynamic learning rate adjustment
- Transfer Learning Integration: Transfer learning orchestration
"""

from .engine import (
    MetaLearningEngine,
    MetaLearningTask,
    MetaLearningResult,
    MetaLearningStrategy
)
from .architecture_search import ModelArchitectureSearch
from .hyperparameter_optimization import HyperparameterOptimizer
from .learning_rate_adaptation import LearningRateAdapter
from .transfer_learning import TransferLearningIntegrator

__all__ = [
    "MetaLearningEngine",
    "MetaLearningTask",
    "MetaLearningResult",
    "MetaLearningStrategy",
    "ModelArchitectureSearch",
    "HyperparameterOptimizer",
    "LearningRateAdapter",
    "TransferLearningIntegrator"
]

__version__ = "1.0.0"
