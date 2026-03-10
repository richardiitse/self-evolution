#!/usr/bin/env python3
"""
Learning Rate Adaptation - FINAL TEST

Tests for Phase 4: Learning Rate Adaptation.
"""

import sys
import random
import math
from pathlib import Path
from datetime import datetime


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metalearning.learning_rate_adaptation import (
    LearningRateAdapter,
    LearningRateScheduler,
    AdaptiveOptimizer,
    LearningRateConfig,
    LearningRateState,
    AdaptationResult
)


def test_schedule_constant():
    """Test constant learning rate schedule."""
    print("🧪 Testing constant schedule...")
    
    adapter = LearningRateAdapter()
    
    initial_lr = 0.001
    params = {}
    
    lr_0 = adapter._schedule_constant(0, initial_lr, params)
    lr_10 = adapter._schedule_constant(10, initial_lr, params)
    lr_100 = adapter._schedule_constant(100, initial_lr, params)
    
    assert lr_0 == initial_lr
    assert lr_10 == initial_lr
    assert lr_100 == initial_lr
    print(f"  ✅ Constant: lr={lr_0:.6f} (constant)")
    
    print("  ✅ Constant schedule tests passed")
    return True


def test_schedule_step():
    """Test step decay learning rate schedule."""
    print("\n🧪 Testing step decay schedule...")
    
    adapter = LearningRateAdapter()
    
    initial_lr = 0.001
    params = {"step_size": 10, "gamma": 0.1}
    
    lr_0 = adapter._schedule_step(0, initial_lr, params)
    lr_5 = adapter._schedule_step(5, initial_lr, params)
    lr_10 = adapter._schedule_step(10, initial_lr, params)
    lr_15 = adapter._schedule_step(15, initial_lr, params)
    
    assert lr_0 == initial_lr
    assert lr_5 == initial_lr
    assert lr_10 == initial_lr * 0.1
    assert lr_15 == initial_lr * 0.1
    print(f"  ✅ Step decay: lr={lr_0:.6f}, {lr_10:.6f}, {lr_15:.6f}")
    
    print("  ✅ Step decay schedule tests passed")
    return True


def test_schedule_exponential():
    """Test exponential decay learning rate schedule."""
    print("\n🧪 Testing exponential decay schedule...")
    
    adapter = LearningRateAdapter()
    
    initial_lr = 0.001
    params = {"gamma": 0.99}
    
    lr_0 = adapter._schedule_exponential(0, initial_lr, params)
    lr_10 = adapter._schedule_exponential(10, initial_lr, params)
    lr_100 = adapter._schedule_exponential(100, initial_lr, params)
    
    assert lr_0 == initial_lr
    assert lr_10 < lr_0
    assert lr_100 < lr_10
    assert lr_100 > 0
    print(f"  ✅ Exponential: lr={lr_0:.6f}, {lr_10:.6f}, {lr_100:.6f}")
    
    print("  ✅ Exponential decay schedule tests passed")
    return True


def test_schedule_cosine():
    """Test cosine annealing learning rate schedule."""
    print("\n🧪 Testing cosine annealing schedule...")
    
    adapter = LearningRateAdapter()
    
    initial_lr = 0.001
    params = {"total_steps": 100, "min_lr": 0.0}
    
    lr_0 = adapter._schedule_cosine(0, initial_lr, params)
    lr_25 = adapter._schedule_cosine(25, initial_lr, params)
    lr_50 = adapter._schedule_cosine(50, initial_lr, params)
    lr_75 = adapter._schedule_cosine(75, initial_lr, params)
    lr_100 = adapter._schedule_cosine(100, initial_lr, params)
    
    assert lr_0 == initial_lr
    assert lr_50 < lr_0
    assert lr_100 == 0.0
    print(f"  ✅ Cosine: lr={lr_0:.6f}, {lr_50:.6f}, {lr_100:.6f}")
    
    print("  ✅ Cosine annealing schedule tests passed")
    return True


def test_schedule_onecycle():
    """Test one-cycle learning rate schedule."""
    print("\n🧪 Testing one-cycle schedule...")
    
    adapter = LearningRateAdapter()
    
    initial_lr = 0.001
    params = {"total_steps": 100, "max_lr": 0.01, "pct_start": 0.3}
    
    lr_0 = adapter._schedule_onecycle(0, initial_lr, params)
    lr_25 = adapter._schedule_onecycle(25, initial_lr, params)
    lr_30 = adapter._schedule_onecycle(30, initial_lr, params)
    lr_50 = adapter._schedule_onecycle(50, initial_lr, params)
    lr_100 = adapter._schedule_onecycle(100, initial_lr, params)
    
    assert lr_0 == initial_lr
    assert lr_30 > lr_0  # Ramp up
    assert lr_100 < lr_50  # Ramp down
    assert lr_100 < lr_0  # Final LR lower than initial
    print(f"  ✅ One-cycle: lr={lr_0:.6f}, {lr_30:.6f}, {lr_50:.6f}, {lr_100:.6f}")
    
    print("  ✅ One-cycle schedule tests passed")
    return True


def test_warmup():
    """Test learning rate warmup."""
    print("\n🧪 Testing warmup...")
    
    adapter = LearningRateAdapter()
    
    config = LearningRateConfig(
        config_id="test",
        name="test",
        initial_lr=0.001,
        schedule_type="constant",
        schedule_params={},
        optimizer_type="adam",
        optimizer_params={},
        warmup_steps=10,
        warmup_lr=0.0001
    )
    
    lr_0 = adapter.get_learning_rate(0, config)
    lr_5 = adapter.get_learning_rate(5, config)
    lr_10 = adapter.get_learning_rate(10, config)
    lr_20 = adapter.get_learning_rate(20, config)
    
    assert lr_0 == config.warmup_lr
    assert lr_5 > lr_0
    assert lr_5 < config.initial_lr
    assert lr_10 == config.initial_lr
    assert lr_20 == config.initial_lr
    print(f"  ✅ Warmup: lr={lr_0:.6f}, {lr_5:.6f}, {lr_10:.6f}, {lr_20:.6f}")
    
    print("  ✅ Warmup tests passed")
    return True


def test_sgd_step():
    """Test SGD optimizer step."""
    print("\n🧪 Testing SGD step...")
    
    adapter = LearningRateAdapter()
    
    state = LearningRateState(
        step=0,
        learning_rate=0.01,
        momentum=0.0,
        velocity=0.0,
        loss=1.0,
        gradient_norm=1.0
    )
    
    gradient = 0.5
    update = adapter._step_sgd(state, gradient)
    
    expected = -state.learning_rate * gradient
    assert abs(update - expected) < 1e-6
    print(f"  ✅ SGD: update={update:.6f}, expected={expected:.6f}")
    
    print("  ✅ SGD step tests passed")
    return True


def test_adam_step():
    """Test Adam optimizer step."""
    print("\n🧪 Testing Adam step...")
    
    adapter = LearningRateAdapter()
    
    state = LearningRateState(
        step=0,
        learning_rate=0.01,
        momentum=0.0,
        velocity=0.0,
        loss=1.0,
        gradient_norm=1.0
    )
    
    gradient = 0.5
    update1 = adapter._step_adam(state, gradient)
    
    # First step should initialize m and v
    assert hasattr(state, '_m')
    assert hasattr(state, '_v')
    assert state._step == 1
    
    # Second step
    update2 = adapter._step_adam(state, gradient)
    assert state._step == 2
    print(f"  ✅ Adam: step 1 update={update1:.6f}, step 2 update={update2:.6f}")
    
    print("  ✅ Adam step tests passed")
    return True


def test_training_simulation():
    """Test training simulation."""
    print("\n🧪 Testing training simulation...")
    
    adapter = LearningRateAdapter()
    
    config = LearningRateConfig(
        config_id="test",
        name="test",
        initial_lr=0.001,
        schedule_type="cosine",
        schedule_params={"total_steps": 100, "min_lr": 0.0},
        optimizer_type="adam",
        optimizer_params={}
    )
    
    result = adapter.simulate_training(config, num_steps=100)
    
    assert result.config_id == config.config_id
    assert result.steps == 100
    assert len(result.lr_history) == 100
    assert len(result.loss_history) == 100
    assert result.final_lr < config.initial_lr
    assert result.final_loss < result.loss_history[0]
    assert result.best_loss <= result.final_loss
    assert result.best_step >= 0
    assert result.convergence_rate >= 0
    print(f"  ✅ Simulation: final_lr={result.final_lr:.6f}, final_loss={result.final_loss:.3f}")
    print(f"     best_loss={result.best_loss:.3f} at step {result.best_step}")
    
    print("  ✅ Training simulation tests passed")
    return True


def test_scheduler():
    """Test LearningRateScheduler."""
    print("\n🧪 Testing LearningRateScheduler...")
    
    scheduler = LearningRateScheduler()
    
    # Create config
    config = scheduler.create_config(
        name="test",
        schedule_type="cosine",
        optimizer_type="adam",
        initial_lr=0.001,
        schedule_params={"total_steps": 100, "min_lr": 0.0}
    )
    
    assert config.name == "test"
    assert config.schedule_type == "cosine"
    assert config.optimizer_type == "adam"
    assert config.initial_lr == 0.001
    print("  ✅ Config created")
    
    # Evaluate schedule
    lr_history, loss_history = scheduler.evaluate_schedule(config, num_steps=100)
    
    assert len(lr_history) == 100
    assert len(loss_history) == 100
    assert lr_history[0] == config.initial_lr
    assert lr_history[-1] < 1e-6  # Very close to 0
    print(f"  ✅ Schedule evaluated: lr from {lr_history[0]:.6f} to {lr_history[-1]:.6f}")
    print(f"     loss from {loss_history[0]:.3f} to {loss_history[-1]:.3f}")
    
    print("  ✅ Scheduler tests passed")
    return True


def test_adaptive_optimizer():
    """Test AdaptiveOptimizer."""
    print("\n🧪 Testing AdaptiveOptimizer...")
    
    try:
        optimizer = AdaptiveOptimizer()
        
        # Create config
        config = optimizer.create_adaptive_config(
            name="test",
            optimizer_type="adam",
            initial_lr=0.001,
            warmup_steps=10
        )
        
        assert config.name == "test"
        assert config.optimizer_type == "adam"
        assert config.initial_lr == 0.001
        assert config.warmup_steps == 10
        print("  ✅ Adaptive config created")
        
        # Train
        result = optimizer.train_with_adaptive_lr(config, num_steps=100)
        
        assert result.config_id == config.config_id
        assert result.steps == 100
        assert result.final_loss < 1.0
        assert len(result.lr_history) == 100
        print(f"  ✅ Training: final_loss={result.final_loss:.3f}")
        
        print("  ✅ Adaptive optimizer tests passed")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Test comparing different schedules."""
    print("\n🧪 Testing schedule comparison...")
    
    scheduler = LearningRateScheduler()
    
    schedules = [
        ("Constant", "constant", {}),
        ("Step", "step", {"step_size": 30, "gamma": 0.1}),
        ("Cosine", "cosine", {"total_steps": 100, "min_lr": 0.0}),
    ]
    
    results = {}
    for name, schedule_type, params in schedules:
        config = scheduler.create_config(
            name=name,
            schedule_type=schedule_type,
            schedule_params=params,
            initial_lr=0.001
        )
        
        lr_history, loss_history = scheduler.evaluate_schedule(config, num_steps=100)
        
        results[name] = {
            "lr": lr_history[-1],
            "loss": loss_history[-1]
        }
        print(f"  ✅ {name}: lr={lr_history[-1]:.6f}, loss={loss_history[-1]:.3f}")
    
    # Check that all schedules worked
    assert len(results) == 3
    print("  ✅ All schedules evaluated successfully")
    
    print("  ✅ Schedule comparison tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    
    print("=" * 70)
    print("📈 Learning Rate Adaptation Tests (Phase 4) - FINAL TEST")
    print("=" * 70)
    print()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    tests = {
        "Constant Schedule": test_schedule_constant,
        "Step Decay Schedule": test_schedule_step,
        "Exponential Decay Schedule": test_schedule_exponential,
        "Cosine Annealing Schedule": test_schedule_cosine,
        "One-Cycle Schedule": test_schedule_onecycle,
        "Warmup": test_warmup,
        "SGD Step": test_sgd_step,
        "Adam Step": test_adam_step,
        "Training Simulation": test_training_simulation,
        "Scheduler": test_scheduler,
        "Adaptive Optimizer": test_adaptive_optimizer,
        "Schedule Comparison": test_comparison,
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
        print("\n🎉 All tests passed! Learning Rate Adaptation component complete.")
        print("   Phase 4: Learning Rate Adaptation - 100% COMPLETE")
        print("   Ready to proceed to: Transfer Learning Integration")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
