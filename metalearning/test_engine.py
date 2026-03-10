#!/usr/bin/env python3
"""
Meta-Learning Engine - FINAL TEST

Tests for Phase 4: Meta-Learning Engine.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import asdict


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metalearning.engine import (
    MetaLearningEngine,
    MetaLearningTask,
    MetaLearningResult,
    MetaLearningStrategy
)


def test_engine_initialization():
    """Test that engine initializes correctly."""
    print("🧪 Testing engine initialization...")
    
    engine = MetaLearningEngine()
    
    # Check storage directory
    assert engine.storage_dir.exists()
    print("  ✅ Storage directory created")
    
    # Check default strategies
    assert len(engine.strategies) == 3
    assert "maml" in engine.strategies
    assert "reptile" in engine.strategies
    assert "baseline" in engine.strategies
    print(f"  ✅ Default strategies initialized: {list(engine.strategies.keys())}")
    
    # Check empty tasks
    assert len(engine.tasks) == 0
    assert len(engine.results) == 0
    print("  ✅ Empty tasks and results")
    
    print("  ✅ Engine initialization tests passed")
    return True


def test_task_creation():
    """Test creating meta-learning tasks."""
    print("\n🧪 Testing task creation...")
    
    engine = MetaLearningEngine()
    
    task1 = engine.create_task(
        name="Test Task 1",
        description="First test task",
        phase="phase4",
        task_type="architecture_search"
    )
    
    # Check task properties
    assert task1.name == "Test Task 1"
    assert task1.phase == "phase4"
    assert task1.task_type == "architecture_search"
    assert task1.status == "pending"
    assert task1.task_id in engine.tasks
    print(f"  ✅ Task created: {task1.task_id}")
    
    task2 = engine.create_task(
        name="Test Task 2",
        description="Second test task",
        phase="phase4",
        task_type="hyperopt"
    )
    
    assert len(engine.tasks) == 2
    print(f"  ✅ Second task created: {task2.task_id}")
    
    print("  ✅ Task creation tests passed")
    return True


def test_task_lifecycle():
    """Test task lifecycle (pending -> running -> completed)."""
    print("\n🧪 Testing task lifecycle...")
    
    engine = MetaLearningEngine()
    
    # Create task
    task = engine.create_task(
        name="Lifecycle Test",
        description="Test task lifecycle",
        phase="phase4",
        task_type="architecture_search"
    )
    
    assert task.status == "pending"
    print("  ✅ Task created in pending state")
    
    # Start task
    success = engine.start_task(task.task_id)
    assert success == True
    task = engine.get_task(task.task_id)
    assert task.status == "running"
    print("  ✅ Task started (pending -> running)")
    
    # Complete task
    success = engine.complete_task(
        task.task_id,
        success=True,
        performance=0.85,
        artifacts={"best_architecture": "cnn_3layer"},
        metrics={"accuracy": 0.85},
        duration=100.0
    )
    assert success == True
    task = engine.get_task(task.task_id)
    assert task.status == "completed"
    assert task.completed_at is not None
    print("  ✅ Task completed (running -> completed)")
    
    # Check result stored
    assert task.task_id in engine.results
    result = engine.results[task.task_id]
    assert result.performance == 0.85
    assert result.success == True
    print("  ✅ Result stored correctly")
    
    print("  ✅ Task lifecycle tests passed")
    return True


def test_task_filtering():
    """Test filtering tasks by phase, status, and type."""
    print("\n🧪 Testing task filtering...")
    
    engine = MetaLearningEngine()
    
    # Create multiple tasks
    engine.create_task("Task 1", "Task 1", "phase4", "architecture_search")
    engine.create_task("Task 2", "Task 2", "phase4", "hyperopt")
    engine.create_task("Task 3", "Task 3", "phase5", "transfer_learning")
    
    # Test phase filter
    phase4_tasks = engine.list_tasks(phase="phase4")
    assert len(phase4_tasks) == 2
    print(f"  ✅ Phase 4 tasks: {len(phase4_tasks)}")
    
    # Test task type filter
    arch_tasks = engine.list_tasks(task_type="architecture_search")
    assert len(arch_tasks) == 1
    print(f"  ✅ Architecture search tasks: {len(arch_tasks)}")
    
    # Test combined filters
    phase4_arch_tasks = engine.list_tasks(phase="phase4", task_type="architecture_search")
    assert len(phase4_arch_tasks) == 1
    print(f"  ✅ Phase 4 architecture search tasks: {len(phase4_arch_tasks)}")
    
    print("  ✅ Task filtering tests passed")
    return True


def test_strategy_selection():
    """Test strategy selection for different tasks."""
    print("\n🧪 Testing strategy selection...")
    
    engine = MetaLearningEngine()
    
    # Test default selection
    strategy = engine.select_strategy("architecture_search")
    assert strategy is not None
    assert strategy.name in ["MAML", "Reptile", "Baseline"]
    print(f"  ✅ Selected strategy: {strategy.name}")
    
    # Test with cost constraint
    strategy = engine.select_strategy("architecture_search", constraints={"max_cost": 0.3})
    assert strategy.cost_estimate <= 0.3
    print(f"  ✅ Selected low-cost strategy: {strategy.name} (cost: {strategy.cost_estimate})")
    
    # Test with performance constraint
    strategy = engine.select_strategy("architecture_search", constraints={"min_performance": 0.8})
    assert strategy.expected_performance >= 0.8
    print(f"  ✅ Selected high-performance strategy: {strategy.name} (performance: {strategy.expected_performance})")
    
    print("  ✅ Strategy selection tests passed")
    return True


def test_performance_tracking():
    """Test performance tracking and summary."""
    print("\n🧪 Testing performance tracking...")
    
    engine = MetaLearningEngine()
    
    # Create and complete tasks
    task1 = engine.create_task("Task 1", "Task 1", "phase4", "architecture_search")
    task2 = engine.create_task("Task 2", "Task 2", "phase4", "hyperopt")
    task3 = engine.create_task("Task 3", "Task 3", "phase4", "architecture_search")
    
    engine.complete_task(task1.task_id, True, 0.85, {}, {"accuracy": 0.85}, 100.0)
    engine.complete_task(task2.task_id, True, 0.78, {}, {"accuracy": 0.78}, 95.0)
    engine.complete_task(task3.task_id, True, 0.90, {}, {"accuracy": 0.90}, 110.0)
    
    # Check performance history
    assert len(engine.performance_history) == 3
    print(f"  ✅ Performance history: {len(engine.performance_history)} entries")
    
    # Check summary
    summary = engine.get_performance_summary()
    assert summary["total_tasks"] == 3
    assert summary["successful_tasks"] == 3
    assert summary["average_performance"] > 0.8
    print(f"  ✅ Average performance: {summary['average_performance']:.2f}")
    print(f"  ✅ Max performance: {summary['max_performance']:.2f}")
    
    # Check by type stats
    assert "architecture_search" in summary["by_type"]
    assert "hyperopt" in summary["by_type"]
    print(f"  ✅ Architecture search tasks: {summary['by_type']['architecture_search']['count']}")
    print(f"  ✅ Hyperopt tasks: {summary['by_type']['hyperopt']['count']}")
    
    print("  ✅ Performance tracking tests passed")
    return True


def test_complete_workflow():
    """Test complete workflow from task creation to completion."""
    print("\n🧪 Testing complete workflow...")
    
    engine = MetaLearningEngine()
    
    # Step 1: Create tasks
    print("  Step 1: Creating tasks...")
    tasks = []
    for i in range(3):
        task = engine.create_task(
            f"Workflow Task {i+1}",
            f"Workflow test task {i+1}",
            "phase4",
            "architecture_search",
            metadata={"iteration": i+1}
        )
        tasks.append(task)
        print(f"    ✅ Created: {task.task_id}")
    
    # Step 2: Start tasks
    print("  Step 2: Starting tasks...")
    for task in tasks:
        engine.start_task(task.task_id)
    print("    ✅ All tasks started")
    
    # Step 3: Complete tasks
    print("  Step 3: Completing tasks...")
    for i, task in enumerate(tasks):
        engine.complete_task(
            task.task_id,
            success=True,
            performance=0.75 + i * 0.05,
            artifacts={"iteration": i+1},
            metrics={"iteration": i+1},
            duration=100.0 + i * 10.0
        )
    print("    ✅ All tasks completed")
    
    # Step 4: List and verify
    print("  Step 4: Verifying results...")
    listed_tasks = engine.list_tasks(phase="phase4", status="completed")
    assert len(listed_tasks) == 3
    print(f"    ✅ Listed {len(listed_tasks)} completed tasks")
    
    # Step 5: Get summary
    print("  Step 5: Getting performance summary...")
    summary = engine.get_performance_summary()
    assert summary["total_tasks"] == 3
    assert summary["average_performance"] > 0.75
    print(f"    ✅ Average performance: {summary['average_performance']:.2f}")
    
    # Step 6: Select strategy for new task
    print("  Step 6: Selecting strategy...")
    strategy = engine.select_strategy("architecture_search")
    assert strategy is not None
    print(f"    ✅ Selected: {strategy.name}")
    
    print("  ✅ Complete workflow tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("🧪 Meta-Learning Engine Tests (Phase 4) - FINAL TEST")
    print("=" * 70)
    print()
    
    tests = {
        "Engine Initialization": test_engine_initialization,
        "Task Creation": test_task_creation,
        "Task Lifecycle": test_task_lifecycle,
        "Task Filtering": test_task_filtering,
        "Strategy Selection": test_strategy_selection,
        "Performance Tracking": test_performance_tracking,
        "Complete Workflow": test_complete_workflow,
    }
    
    results = {}
    for name, test_func in tests.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Meta-Learning Engine component complete.")
        print("   Phase 4: Meta-Learning Engine - 100% COMPLETE")
        print("   Ready to proceed to: Model Architecture Search")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
