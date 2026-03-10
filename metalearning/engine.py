#!/usr/bin/env python3
"""
Phase 4: Meta-Learning Engine

The main orchestrator for meta-learning across all phases and tasks.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
import hashlib


# ==================== Domain Classes ====================

@dataclass
class MetaLearningTask:
    """Represents a meta-learning task."""
    
    task_id: str
    name: str
    description: str
    phase: str
    task_type: str  # "architecture_search", "hyperopt", "transfer_learning", etc.
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "running", "completed", "failed"
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "task_type": self.task_type,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "metadata": self.metadata,
            "results": self.results
        }


@dataclass
class MetaLearningResult:
    """Stores the outcome of a meta-learning task."""
    
    task_id: str
    success: bool
    performance: float  # 0.0 to 1.0
    duration: float  # seconds
    artifacts: Dict[str, Any]  # learned models, parameters, etc.
    metrics: Dict[str, float]  # additional metrics
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "performance": self.performance,
            "duration": self.duration,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MetaLearningStrategy:
    """Defines a meta-learning strategy."""
    
    name: str
    description: str
    algorithm: str  # "maml", "reptile", "baseline", etc.
    parameters: Dict[str, Any]
    expected_performance: float
    cost_estimate: float  # computational cost
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "algorithm": self.algorithm,
            "parameters": self.parameters,
            "expected_performance": self.expected_performance,
            "cost_estimate": self.cost_estimate
        }


# ==================== Meta-Learning Engine ====================

class MetaLearningEngine:
    """
    Main orchestrator for meta-learning across all phases.
    
    Features:
    - Meta-learning task management
    - Meta-data collection and storage
    - Cross-task learning strategy selection
    - Performance tracking and evaluation
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".metalearning"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Task storage
        self.tasks: Dict[str, MetaLearningTask] = {}
        self.results: Dict[str, MetaLearningResult] = {}
        
        # Strategies
        self.strategies: Dict[str, MetaLearningStrategy] = {}
        self._init_default_strategies()
        
        # Performance history
        self.performance_history: List[Dict[str, Any]] = []
    
    def _init_default_strategies(self):
        """Initialize default meta-learning strategies."""
        self.strategies["maml"] = MetaLearningStrategy(
            name="MAML",
            description="Model-Agnostic Meta-Learning",
            algorithm="maml",
            parameters={
                "inner_lr": 0.01,
                "outer_lr": 0.001,
                "num_inner_steps": 5,
                "num_outer_steps": 1000
            },
            expected_performance=0.85,
            cost_estimate=1.0
        )
        
        self.strategies["reptile"] = MetaLearningStrategy(
            name="Reptile",
            description="First-Order MAML",
            algorithm="reptile",
            parameters={
                "inner_lr": 0.1,
                "outer_lr": 0.1,
                "num_inner_steps": 5,
                "num_outer_steps": 10000
            },
            expected_performance=0.75,
            cost_estimate=0.5
        )
        
        self.strategies["baseline"] = MetaLearningStrategy(
            name="Baseline",
            description="Standard learning from scratch",
            algorithm="baseline",
            parameters={
                "learning_rate": 0.001,
                "epochs": 1000
            },
            expected_performance=0.60,
            cost_estimate=0.2
        )
    
    def generate_task_id(self, name: str) -> str:
        """Generate a unique task ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{name}_{timestamp}"
        hash_obj = hashlib.md5(hash_input.encode())
        return f"task_{hash_obj.hexdigest()[:8]}"
    
    def create_task(
        self,
        name: str,
        description: str,
        phase: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MetaLearningTask:
        """
        Create a new meta-learning task.
        
        Args:
            name: Task name
            description: Task description
            phase: Phase identifier (e.g., "phase4")
            task_type: Type of meta-learning task
            metadata: Additional metadata
        
        Returns:
            Created MetaLearningTask
        """
        task_id = self.generate_task_id(name)
        
        task = MetaLearningTask(
            task_id=task_id,
            name=name,
            description=description,
            phase=phase,
            task_type=task_type,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        self._save_task(task)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[MetaLearningTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(
        self,
        phase: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[MetaLearningTask]:
        """
        List tasks with optional filters.
        
        Args:
            phase: Filter by phase
            status: Filter by status
            task_type: Filter by task type
        
        Returns:
            List of matching tasks
        """
        tasks = list(self.tasks.values())
        
        if phase:
            tasks = [t for t in tasks if t.phase == phase]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)
    
    def start_task(self, task_id: str) -> bool:
        """
        Start a meta-learning task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if task started successfully
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status != "pending":
            return False
        
        task.status = "running"
        self._save_task(task)
        
        return True
    
    def complete_task(
        self,
        task_id: str,
        success: bool,
        performance: float,
        artifacts: Dict[str, Any],
        metrics: Dict[str, Any],
        duration: float
    ) -> bool:
        """
        Complete a meta-learning task.
        
        Args:
            task_id: Task ID
            success: Whether task succeeded
            performance: Performance score (0.0 to 1.0)
            artifacts: Learned artifacts
            metrics: Additional metrics
            duration: Task duration in seconds
        
        Returns:
            True if task completed successfully
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Update task
        task.status = "completed" if success else "failed"
        task.completed_at = datetime.now()
        task.results = {
            "success": success,
            "performance": performance,
            "artifacts": artifacts,
            "metrics": metrics
        }
        
        # Create result
        result = MetaLearningResult(
            task_id=task_id,
            success=success,
            performance=performance,
            duration=duration,
            artifacts=artifacts,
            metrics=metrics,
            timestamp=datetime.now()
        )
        
        self.results[task_id] = result
        self._save_task(task)
        self._save_result(result)
        
        # Update performance history
        self.performance_history.append({
            "task_id": task_id,
            "task_name": task.name,
            "task_type": task.task_type,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def select_strategy(self, task_type: str, constraints: Optional[Dict[str, Any]] = None) -> Optional[MetaLearningStrategy]:
        """
        Select the best meta-learning strategy for a task.
        
        Args:
            task_type: Type of task
            constraints: Constraints (e.g., max_cost, min_performance)
        
        Returns:
            Selected strategy or None
        """
        constraints = constraints or {}
        
        # Filter strategies by task type
        candidate_strategies = {}
        for name, strategy in self.strategies.items():
            # Simple matching - in reality this would be more sophisticated
            if task_type in ["architecture_search", "hyperopt", "transfer_learning"]:
                candidate_strategies[name] = strategy
        
        if not candidate_strategies:
            # Fallback to all strategies
            candidate_strategies = self.strategies.copy()
        
        # Apply constraints
        valid_strategies = {}
        for name, strategy in candidate_strategies.items():
            valid = True
            
            # Check cost constraint
            if "max_cost" in constraints and strategy.cost_estimate > constraints["max_cost"]:
                valid = False
            
            # Check performance constraint
            if "min_performance" in constraints and strategy.expected_performance < constraints["min_performance"]:
                valid = False
            
            if valid:
                valid_strategies[name] = strategy
        
        if not valid_strategies:
            # No strategies meet constraints, return best available
            return max(candidate_strategies.values(), key=lambda x: x.expected_performance)
        
        # Return strategy with highest expected performance
        return max(valid_strategies.values(), key=lambda x: x.expected_performance)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance history.
        
        Returns:
            Performance summary statistics
        """
        if not self.performance_history:
            return {
                "total_tasks": 0,
                "successful_tasks": 0,
                "average_performance": 0.0,
                "by_type": {}
            }
        
        successful_tasks = [h for h in self.performance_history if h.get("success", True)]
        
        # Group by task type
        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for entry in self.performance_history:
            task_type = entry["task_type"]
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(entry)
        
        # Calculate statistics
        type_stats = {}
        for task_type, entries in by_type.items():
            performances = [e["performance"] for e in entries]
            type_stats[task_type] = {
                "count": len(performances),
                "average_performance": sum(performances) / len(performances) if performances else 0.0,
                "max_performance": max(performances) if performances else 0.0
            }
        
        overall_performance = [h["performance"] for h in self.performance_history]
        
        return {
            "total_tasks": len(self.performance_history),
            "successful_tasks": len(successful_tasks),
            "average_performance": sum(overall_performance) / len(overall_performance) if overall_performance else 0.0,
            "max_performance": max(overall_performance) if overall_performance else 0.0,
            "min_performance": min(overall_performance) if overall_performance else 0.0,
            "by_type": type_stats
        }
    
    def _save_task(self, task: MetaLearningTask):
        """Save task to storage."""
        task_file = self.storage_dir / f"task_{task.task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, indent=2)
    
    def _save_result(self, result: MetaLearningResult):
        """Save result to storage."""
        result_file = self.storage_dir / f"result_{result.task_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)


# ==================== Main ====================

def main():
    """Simple demo of Meta-Learning Engine."""
    print("=" * 70)
    print("🧠 Meta-Learning Engine - Demo")
    print("=" * 70)
    print()
    
    # Create engine
    engine = MetaLearningEngine()
    
    # Create tasks
    print("📋 Creating meta-learning tasks...")
    
    task1 = engine.create_task(
        name="Architecture Search Test",
        description="Test NAS algorithm on sample task",
        phase="phase4",
        task_type="architecture_search",
        metadata={"search_space": "cnn", "dataset": "mnist"}
    )
    print(f"  ✅ Created task: {task1.task_id} - {task1.name}")
    
    task2 = engine.create_task(
        name="Hyperparameter Optimization Test",
        description="Test hyperparameter optimization on sample task",
        phase="phase4",
        task_type="hyperopt",
        metadata={"search_space": "mlp", "dataset": "cifar10"}
    )
    print(f"  ✅ Created task: {task2.task_id} - {task2.name}")
    
    # Start tasks
    print("\n🚀 Starting tasks...")
    engine.start_task(task1.task_id)
    engine.start_task(task2.task_id)
    print("  ✅ Tasks started")
    
    # Complete tasks
    print("\n✅ Completing tasks...")
    
    engine.complete_task(
        task1.task_id,
        success=True,
        performance=0.85,
        artifacts={"best_architecture": "cnn_3layer"},
        metrics={"accuracy": 0.85, "loss": 0.15},
        duration=120.5
    )
    
    engine.complete_task(
        task2.task_id,
        success=True,
        performance=0.78,
        artifacts={"best_params": {"lr": 0.001, "batch_size": 32}},
        metrics={"accuracy": 0.78, "loss": 0.22},
        duration=95.3
    )
    
    print("  ✅ Tasks completed")
    
    # List tasks
    print("\n📊 Listing tasks...")
    tasks = engine.list_tasks(phase="phase4")
    print(f"  Total tasks: {len(tasks)}")
    for task in tasks:
        print(f"    - {task.name}: {task.status} (performance: {task.results.get('performance', 0.0):.2f})")
    
    # Select strategy
    print("\n🎯 Selecting strategy for architecture search...")
    strategy = engine.select_strategy("architecture_search")
    print(f"  ✅ Selected: {strategy.name} (expected performance: {strategy.expected_performance:.2f})")
    
    # Performance summary
    print("\n📈 Performance summary...")
    summary = engine.get_performance_summary()
    print(f"  Total tasks: {summary['total_tasks']}")
    print(f"  Successful tasks: {summary['successful_tasks']}")
    print(f"  Average performance: {summary['average_performance']:.2f}")
    print(f"  Max performance: {summary['max_performance']:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ Meta-Learning Engine demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
