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
- ThreeLayerMemorySystem: Three-layer memory architecture for autonomous evolution
- MemoryDrivenEvolution: Evidence-based evolution options from memory analysis

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

# NEW: 导出三层记忆系统
from .three_layer_memory import (
    SoulLayerMemory,
    LongTermMemory,
    LogEntry as MemoryLogEntry,
    MemorySnapshot,
    ConsolidationResult,
    SoulLayerReader,
    LongTermMemoryLayer,
    LogLayer,
    ThreeLayerMemorySystem
)

# NEW: 导出记忆驱动进化
from .memory_driven_evolution import (
    EvolutionOption,
    MemoryAnalysisResult,
    EvolutionExecutionResult,
    MemoryDrivenEvolution,
    EvidenceSource
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
    # NEW: Three-Layer Memory
    "SoulLayerMemory",
    "LongTermMemory",
    "MemorySnapshot",
    "ConsolidationResult",
    "SoulLayerReader",
    "LongTermMemoryLayer",
    "LogLayer",
    "ThreeLayerMemorySystem",
    # NEW: Memory-Driven Evolution
    "EvolutionOption",
    "MemoryAnalysisResult",
    "EvolutionExecutionResult",
    "MemoryDrivenEvolution",
    "EvidenceSource",
    # Common
    "ValidationResult"
]

__version__ = "1.1.0"