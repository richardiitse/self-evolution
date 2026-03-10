#!/usr/bin/env python3
"""
Multi-Task Learning - FINAL TEST

Tests for Phase 5: Multi-Task Learning.
"""

import sys
import random
import math
from pathlib import Path
from datetime import datetime


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from advanced.multi_task_learning import (
    MultiTaskLearner,
    TaskDefinition,
    SharedLayer,
    TaskSpecificLayer,
    MultiTaskResult
)


def test_learner_initialization():
    """Test that learner initializes correctly."""
    print("🧪 Testing learner initialization...")
    
    learner = MultiTaskLearner(shared_dim=128)
    
    # Check state
    assert learner.shared_dim == 128
    assert len(learner.tasks) == 0
    assert len(learner.shared_layers) == 0
    assert len(learner.task_specific_layers) == 0
    print("  ✅ Learner initialized with shared_dim=128")
    
    print("  ✅ Learner initialization tests passed")
    return True


def test_add_task():
    """Test adding tasks."""
    print("\n🧪 Testing add task...")
    
    learner = MultiTaskLearner()
    
    # Add first task
    task1 = learner.add_task(
        name="Classification",
        input_dim=100,
        output_dim=10,
        task_type="classification",
        loss_weight=1.0
    )
    
    assert task1.name == "Classification"
    assert task1.input_dim == 100
    assert task1.output_dim == 10
    assert task1.task_type == "classification"
    assert task1.loss_weight == 1.0
    assert task1.task_id in learner.tasks
    print(f"  ✅ Added task: {task1.name}")
    
    # Add second task
    task2 = learner.add_task(
        name="Regression",
        input_dim=50,
        output_dim=1,
        task_type="regression",
        loss_weight=0.5
    )
    
    assert task2.name == "Regression"
    assert task2.task_type == "regression"
    assert task2.task_id in learner.tasks
    print(f"  ✅ Added task: {task2.name}")
    
    # Check task-specific layers created
    assert len(learner.task_specific_layers) == 2
    print("  ✅ Task-specific layers created")
    
    print("  ✅ Add task tests passed")
    return True


def test_shared_layers_initialization():
    """Test shared layers initialization."""
    print("\n🧪 Testing shared layers initialization...")
    
    learner = MultiTaskLearner(shared_dim=64)
    
    # Initialize shared layers
    learner._initialize_shared_layers(input_dim=100, num_shared=2)
    
    assert len(learner.shared_layers) == 2
    print("  ✅ Created 2 shared layers")
    
    # Check layer properties
    for i, layer in enumerate(learner.shared_layers):
        assert layer.layer_id == f"shared_{i}"
        assert layer.input_dim == 100 if i == 0 else 64
        assert layer.output_dim == 64
        assert layer.activation == "relu"
        print(f"  ✅ Layer {i}: {layer.name} ({layer.input_dim} → {layer.output_dim})")
    
    print("  ✅ Shared layers initialization tests passed")
    return True


def test_forward_pass():
    """Test forward pass."""
    print("\n🧪 Testing forward pass...")
    
    learner = MultiTaskLearner(shared_dim=32)
    learner.add_task("Task1", 10, 2, "classification")
    learner._initialize_shared_layers(input_dim=10, num_shared=2)
    
    # Forward pass
    inputs = [random.uniform(0, 1) for _ in range(10)]
    outputs, activations = learner._forward_pass(inputs, list(learner.tasks.keys())[0])
    
    assert len(outputs) == 2
    assert sum(outputs) > 0.99  # Softmax normalization
    assert sum(outputs) < 1.01
    assert len(activations) == 3  # 2 shared + 1 task-specific
    print(f"  ✅ Forward pass: {len(outputs)} outputs, {len(activations)} activations")
    
    print("  ✅ Forward pass tests passed")
    return True


def test_train_single_task():
    """Test training single task."""
    print("\n🧪 Testing train single task...")
    
    learner = MultiTaskLearner(shared_dim=64)
    task = learner.add_task("TestTask", 10, 2, "classification")
    
    # Generate data
    inputs = [[random.uniform(0, 1) for _ in range(10)] for _ in range(50)]
    targets = [[1.0, 0.0] if random.random() > 0.5 else [0.0, 1.0] for _ in range(50)]
    task_data = {task.task_id: (inputs, targets)}
    
    # Train
    result = learner.train_tasks(
        task_data=task_data,
        num_epochs=20,
        learning_rate=0.01
    )
    
    assert result.epochs == 20
    assert len(result.task_results) == 1
    assert result.training_time > 0
    print(f"  ✅ Training completed in {result.training_time:.2f}s")
    
    # Check task results
    task_result = result.task_results[task.task_id]
    assert "loss" in task_result
    assert "accuracy" in task_result
    assert 0.0 <= task_result["accuracy"] <= 1.0
    print(f"  ✅ Task loss: {task_result['loss']:.3f}, accuracy: {task_result['accuracy']:.3f}")
    
    print("  ✅ Train single task tests passed")
    return True


def test_train_multiple_tasks():
    """Test training multiple tasks."""
    print("\n🧪 Testing train multiple tasks...")
    
    learner = MultiTaskLearner(shared_dim=128)
    
    # Add tasks
    task1 = learner.add_task("Task1", 50, 5, "classification", loss_weight=1.0)
    task2 = learner.add_task("Task2", 30, 3, "classification", loss_weight=0.8)
    task3 = learner.add_task("Task3", 20, 1, "regression", loss_weight=0.6)
    
    # Generate data
    inputs1 = [[random.uniform(0, 1) for _ in range(50)] for _ in range(50)]
    targets1 = [[1.0 if i == random.randint(0, 4) else 0.0 for i in range(5)] for _ in range(50)]
    
    inputs2 = [[random.uniform(0, 1) for _ in range(30)] for _ in range(50)]
    targets2 = [[1.0, 0.0, 0.0] if i % 3 == 0 else [0.0, 1.0, 0.0] if i % 3 == 1 else [0.0, 0.0, 1.0] 
                for i in range(50)]
    
    inputs3 = [[random.uniform(0, 1) for _ in range(20)] for _ in range(50)]
    targets3 = [[random.uniform(0, 1)] for _ in range(50)]
    
    task_data = {
        task1.task_id: (inputs1, targets1),
        task2.task_id: (inputs2, targets2),
        task3.task_id: (inputs3, targets3)
    }
    
    # Train
    result = learner.train_tasks(
        task_data=task_data,
        num_epochs=30,
        learning_rate=0.01,
        balance_tasks=True
    )
    
    assert len(result.task_results) == 3
    assert result.training_time > 0
    print(f"  ✅ Training completed in {result.training_time:.2f}s")
    
    # Check all tasks trained
    for task_id in [task1.task_id, task2.task_id, task3.task_id]:
        assert task_id in result.task_results
        print(f"  ✅ {learner.tasks[task_id].name}: loss={result.task_results[task_id]['loss']:.3f}")
    
    print("  ✅ Train multiple tasks tests passed")
    return True


def test_task_balancing():
    """Test task balancing."""
    print("\n🧪 Testing task balancing...")
    
    learner = MultiTaskLearner(shared_dim=64)
    
    # Add tasks with different weights
    task1 = learner.add_task("ImportantTask", 20, 2, "classification", loss_weight=2.0)
    task2 = learner.add_task("LessImportantTask", 20, 2, "classification", loss_weight=0.5)
    
    # Generate data
    inputs = [[random.uniform(0, 1) for _ in range(20)] for _ in range(50)]
    targets1 = [[1.0, 0.0] if i % 2 == 0 else [0.0, 1.0] for i in range(50)]
    targets2 = [[1.0, 0.0] if i % 2 == 0 else [0.0, 1.0] for i in range(50)]
    
    task_data = {
        task1.task_id: (inputs, targets1),
        task2.task_id: (inputs, targets2)
    }
    
    # Train with balancing
    result = learner.train_tasks(
        task_data=task_data,
        num_epochs=20,
        learning_rate=0.01,
        balance_tasks=True
    )
    
    # Check weights
    assert len(result.task_importance_weights) == 2
    total_weight = sum(result.task_importance_weights.values())
    assert abs(total_weight - 1.0) < 0.01
    print(f"  ✅ Task weights: {result.task_importance_weights}")
    
    print("  ✅ Task balancing tests passed")
    return True


def test_evaluate_task():
    """Test task evaluation."""
    print("\n🧪 Testing evaluate task...")
    
    learner = MultiTaskLearner(shared_dim=64)
    task = learner.add_task("EvalTask", 10, 2, "classification")
    
    # Generate data
    inputs = [[random.uniform(0, 1) for _ in range(10)] for _ in range(50)]
    targets = [[1.0, 0.0] if i % 2 == 0 else [0.0, 1.0] for i in range(50)]
    
    # Train
    task_data = {task.task_id: (inputs, targets)}
    learner.train_tasks(task_data=task_data, num_epochs=10, learning_rate=0.01)
    
    # Evaluate
    test_inputs = inputs[:10]
    test_targets = targets[:10]
    metrics = learner.evaluate_task(task.task_id, test_inputs, test_targets)
    
    assert "loss" in metrics
    assert "accuracy" in metrics
    assert 0.0 <= metrics["loss"] <= 1.0
    assert 0.0 <= metrics["accuracy"] <= 1.0
    print(f"  ✅ Evaluation: loss={metrics['loss']:.3f}, accuracy={metrics['accuracy']:.3f}")
    
    print("  ✅ Evaluate task tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    
    print("=" * 70)
    print("🧩 Multi-Task Learning Tests (Phase 5) - FINAL TEST")
    print("=" * 70)
    print()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    tests = {
        "Learner Initialization": test_learner_initialization,
        "Add Task": test_add_task,
        "Shared Layers Initialization": test_shared_layers_initialization,
        "Forward Pass": test_forward_pass,
        "Train Single Task": test_train_single_task,
        "Train Multiple Tasks": test_train_multiple_tasks,
        "Task Balancing": test_task_balancing,
        "Evaluate Task": test_evaluate_task,
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
        print("\n🎉 All tests passed! Multi-Task Learning component complete.")
        print("   Phase 5: Multi-Task Learning - 100% COMPLETE")
        print("   Ready to proceed to: Continual Learning")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
