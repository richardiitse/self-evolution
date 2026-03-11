#!/usr/bin/env python3
"""
Evolution Core - Safe Self-Modification Components

Based on MIRI corrigibility research: implements safe code modification with
robust validation, rollback capabilities, and safety constraints.

Components:
- EvolutionCycle: 7-step evolution process (OBSERVE, ANALYZE, PLAN, EXECUTE, TEST, DOCUMENT, VALIDATE)
- SafetyValidator: MIRI safety constraint validation
- RollbackManager: Backup and restore capabilities
- ResourceController: Resource allocation and monitoring
- EvolutionLog: Complete audit tracking
- LogEntry: Individual log entries
- LogAnalyzer: Pattern extraction from logs
- LogArchiver: Old log compression
- ModificationPlan: Safe modification protocol
- CodeModifier: Code change application
- ChangeValidator: Change validation with corrigibility
- ChangeApplicator: Apply changes with rollback

Research:
- Soares et al. (2015) "Corrigibility"
- MIRI: Safe Self-Modification principles
"""

from .evolution_cycle import (
    EvolutionEvent,
    EvolutionResult,
    EvolutionCycle,
    SafetyValidator,
    RollbackManager,
    ResourceController,
    ValidationResult,
    ResourceStatus
)

from .evolution_log import (
    LogEntry,
    EvolutionPattern,
    EvolutionLog,
    LogAnalyzer,
    LogArchiver,
    EvolutionAnalysis
)

from .modification import (
    ModificationType,
    SafetyConstraint,
    ModificationPlan,
    ModificationResult,
    ValidationResult,
    CodeModifier,
    ChangeValidator,
    ChangeApplicator
)

__all__ = [
    # Evolution Cycle
    "EvolutionEvent",
    "EvolutionResult",
    "EvolutionCycle",
    "SafetyValidator",
    "RollbackManager",
    "ResourceController",
    "ResourceStatus",
    # Evolution Log
    "LogEntry",
    "EvolutionPattern",
    "EvolutionLog",
    "LogAnalyzer",
    "LogArchiver",
    "EvolutionAnalysis",
    # Modification
    "ModificationType",
    "SafetyConstraint",
    "ModificationPlan",
    "ModificationResult",
    "CodeModifier",
    "ChangeValidator",
    "ChangeApplicator",
    # Common
    "ValidationResult"
]

__version__ = "1.0.0"