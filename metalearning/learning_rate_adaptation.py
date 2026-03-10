#!/usr/bin/env python3
"""
Phase 4: Learning Rate Adaptation

Dynamic learning rate adjustment during training for better convergence.
"""

import sys
import random
import math
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
import json


# ==================== Domain Classes ====================

@dataclass
class LearningRateState:
    """State of learning rate during training."""
    
    step: int
    learning_rate: float
    momentum: float
    velocity: float  # For momentum-based methods
    loss: float
    gradient_norm: float
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "learning_rate": self.learning_rate,
            "momentum": self.momentum,
            "velocity": self.velocity,
            "loss": self.loss,
            "gradient_norm": self.gradient_norm,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class LearningRateConfig:
    """Configuration for learning rate adaptation."""
    
    config_id: str
    name: str
    initial_lr: float
    schedule_type: str  # "constant", "step", "exponential", "cosine", "onecycle"
    schedule_params: Dict[str, Any]
    optimizer_type: str  # "sgd", "momentum", "adam", "rmsprop"
    optimizer_params: Dict[str, Any]
    warmup_steps: int = 0
    warmup_lr: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "name": self.name,
            "initial_lr": self.initial_lr,
            "schedule_type": self.schedule_type,
            "schedule_params": self.schedule_params,
            "optimizer_type": self.optimizer_type,
            "optimizer_params": self.optimizer_params,
            "warmup_steps": self.warmup_steps,
            "warmup_lr": self.warmup_lr
        }


@dataclass
class AdaptationResult:
    """Result of learning rate adaptation."""
    
    config_id: str
    final_lr: float
    final_loss: float
    steps: int
    time_taken: float  # seconds
    convergence_rate: float
    best_loss: float
    best_step: int
    lr_history: List[float]
    loss_history: List[float]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "final_lr": self.final_lr,
            "final_loss": self.final_loss,
            "steps": self.steps,
            "time_taken": self.time_taken,
            "convergence_rate": self.convergence_rate,
            "best_loss": self.best_loss,
            "best_step": self.best_step,
            "lr_history": self.lr_history,
            "loss_history": self.loss_history,
            "timestamp": self.timestamp.isoformat()
        }


# ==================== Learning Rate Adaptation ====================

class LearningRateAdapter:
    """
    Dynamic learning rate adjustment during training.
    
    Features:
    - Multiple scheduling strategies (constant, step, exponential, cosine, onecycle)
    - Adaptive optimizers (SGD, Momentum, Adam, RMSprop)
    - Learning rate warmup
    - Gradient-based adjustment
    """
    
    def __init__(self):
        # Scheduling strategies
        self.schedulers = {
            "constant": self._schedule_constant,
            "step": self._schedule_step,
            "exponential": self._schedule_exponential,
            "cosine": self._schedule_cosine,
            "onecycle": self._schedule_onecycle,
        }
        
        # Optimizer step functions
        self.optimizer_steps = {
            "sgd": self._step_sgd,
            "momentum": self._step_momentum,
            "adam": self._step_adam,
            "rmsprop": self._step_rmsprop,
        }
    
    def _schedule_constant(
        self,
        step: int,
        initial_lr: float,
        params: Dict[str, Any]
    ) -> float:
        """Constant learning rate."""
        return initial_lr
    
    def _schedule_step(
        self,
        step: int,
        initial_lr: float,
        params: Dict[str, Any]
    ) -> float:
        """Step decay learning rate schedule."""
        step_size = params.get("step_size", 100)
        gamma = params.get("gamma", 0.1)
        
        return initial_lr * (gamma ** (step // step_size))
    
    def _schedule_exponential(
        self,
        step: int,
        initial_lr: float,
        params: Dict[str, Any]
    ) -> float:
        """Exponential decay learning rate schedule."""
        gamma = params.get("gamma", 0.99)
        
        return initial_lr * (gamma ** step)
    
    def _schedule_cosine(
        self,
        step: int,
        initial_lr: float,
        params: Dict[str, Any]
    ) -> float:
        """Cosine annealing learning rate schedule."""
        total_steps = params.get("total_steps", 1000)
        min_lr = params.get("min_lr", 0.0)
        
        if step >= total_steps:
            return min_lr
        
        return min_lr + (initial_lr - min_lr) * 0.5 * (
            1.0 + math.cos(math.pi * step / total_steps)
        )
    
    def _schedule_onecycle(
        self,
        step: int,
        initial_lr: float,
        params: Dict[str, Any]
    ) -> float:
        """One-cycle learning rate schedule."""
        total_steps = params.get("total_steps", 1000)
        max_lr = params.get("max_lr", initial_lr * 10)
        pct_start = params.get("pct_start", 0.3)
        
        if step >= total_steps:
            return initial_lr * 0.01  # Return to very low LR
        
        step_pct = step / total_steps
        
        if step_pct < pct_start:
            # Ramp up
            lr = initial_lr + (max_lr - initial_lr) * (step_pct / pct_start)
        else:
            # Ramp down
            lr = max_lr - (max_lr - initial_lr * 0.01) * ((step_pct - pct_start) / (1.0 - pct_start))
        
        return lr
    
    def _step_sgd(
        self,
        state: LearningRateState,
        gradient: float
    ) -> float:
        """SGD optimizer step."""
        return -state.learning_rate * gradient
    
    def _step_momentum(
        self,
        state: LearningRateState,
        gradient: float,
        beta: float = 0.9
    ) -> float:
        """Momentum optimizer step."""
        state.velocity = beta * state.velocity - state.learning_rate * gradient
        return state.velocity
    
    def _step_adam(
        self,
        state: LearningRateState,
        gradient: float,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8
    ) -> float:
        """Adam optimizer step."""
        if not hasattr(state, '_m'):
            state._m = 0.0
            state._v = 0.0
            state._step = 0
        
        state._m = beta1 * state._m + (1 - beta1) * gradient
        state._v = beta2 * state._v + (1 - beta2) * gradient ** 2
        
        state._step += 1
        
        m_hat = state._m / (1 - beta1 ** state._step)
        v_hat = state._v / (1 - beta2 ** state._step)
        
        return -state.learning_rate * m_hat / (math.sqrt(v_hat) + epsilon)
    
    def _step_rmsprop(
        self,
        state: LearningRateState,
        gradient: float,
        alpha: float = 0.99,
        epsilon: float = 1e-8
    ) -> float:
        """RMSprop optimizer step."""
        if not hasattr(state, '_v'):
            state._v = 0.0
        
        state._v = alpha * state._v + (1 - alpha) * gradient ** 2
        
        return -state.learning_rate * gradient / (math.sqrt(state._v) + epsilon)
    
    def get_learning_rate(
        self,
        step: int,
        config: LearningRateConfig
    ) -> float:
        """
        Get learning rate at given step.
        
        Args:
            step: Current training step
            config: Learning rate configuration
        
        Returns:
            Learning rate
        """
        # Get scheduled learning rate
        schedule_func = self.schedulers.get(config.schedule_type, self._schedule_constant)
        lr = schedule_func(step, config.initial_lr, config.schedule_params)
        
        # Apply warmup
        if step < config.warmup_steps:
            lr = config.warmup_lr + (lr - config.warmup_lr) * (step / config.warmup_steps)
        
        return lr
    
    def simulate_training(
        self,
        config: LearningRateConfig,
        num_steps: int = 100,
        target_loss: float = 0.1
    ) -> AdaptationResult:
        """
        Simulate training with learning rate schedule (simulation).
        
        Args:
            config: Learning rate configuration
            num_steps: Number of training steps
            target_loss: Target loss value
        
        Returns:
            AdaptationResult
        """
        # Initialize state
        state = LearningRateState(
            step=0,
            learning_rate=config.initial_lr,
            momentum=0.0,
            velocity=0.0,
            loss=1.0,  # Initial loss
            gradient_norm=1.0
        )
        
        lr_history = []
        loss_history = []
        best_loss = float('inf')
        best_step = 0
        
        # Simulate training
        for step in range(num_steps):
            state.step = step
            
            # Update learning rate
            state.learning_rate = self.get_learning_rate(step, config)
            
            # Simulate loss (decay towards target)
            # Decay depends on learning rate (too high or too low = slow decay)
            optimal_lr = 0.01  # Simulated optimal LR
            lr_ratio = state.learning_rate / optimal_lr
            
            # Loss decay factor (optimal LR = fastest decay)
            decay_factor = 0.995 / (1.0 + abs(lr_ratio - 1.0))
            state.loss = state.loss * decay_factor + random.uniform(-0.01, 0.01)
            state.loss = max(target_loss, min(1.0, state.loss))
            
            # Simulate gradient
            state.gradient_norm = state.loss * 0.5 + random.uniform(-0.1, 0.1)
            state.gradient_norm = max(0.0, state.gradient_norm)
            
            # Record history
            lr_history.append(state.learning_rate)
            loss_history.append(state.loss)
            
            # Track best
            if state.loss < best_loss:
                best_loss = state.loss
                best_step = step
        
        # Calculate convergence rate
        final_loss = loss_history[-1]
        convergence_rate = (loss_history[0] - final_loss) / loss_history[0]
        
        # Create result
        result = AdaptationResult(
            config_id=config.config_id,
            final_lr=lr_history[-1],
            final_loss=final_loss,
            steps=num_steps,
            time_taken=num_steps * 0.1,  # Simulated time
            convergence_rate=convergence_rate,
            best_loss=best_loss,
            best_step=best_step,
            lr_history=lr_history,
            loss_history=loss_history
        )
        
        return result


# ==================== Learning Rate Scheduler ====================

class LearningRateScheduler:
    """
    Manages learning rate schedules for training.
    
    Features:
    - Multiple scheduling strategies
    - Learning rate warmup
    - Schedule visualization
    """
    
    def __init__(self):
        self.adapter = LearningRateAdapter()
    
    def create_config(
        self,
        name: str,
        schedule_type: str = "cosine",
        optimizer_type: str = "adam",
        initial_lr: float = 0.001,
        schedule_params: Optional[Dict[str, Any]] = None,
        optimizer_params: Optional[Dict[str, Any]] = None,
        warmup_steps: int = 0
    ) -> LearningRateConfig:
        """
        Create a learning rate configuration.
        
        Args:
            name: Configuration name
            schedule_type: Type of schedule
            optimizer_type: Type of optimizer
            initial_lr: Initial learning rate
            schedule_params: Schedule parameters
            optimizer_params: Optimizer parameters
            warmup_steps: Number of warmup steps
        
        Returns:
            LearningRateConfig
        """
        config_id = f"lr_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        schedule_params = schedule_params or {}
        optimizer_params = optimizer_params or {}
        
        config = LearningRateConfig(
            config_id=config_id,
            name=name,
            initial_lr=initial_lr,
            schedule_type=schedule_type,
            schedule_params=schedule_params,
            optimizer_type=optimizer_type,
            optimizer_params=optimizer_params,
            warmup_steps=warmup_steps,
            warmup_lr=initial_lr * 0.1
        )
        
        return config
    
    def evaluate_schedule(
        self,
        config: LearningRateConfig,
        num_steps: int = 100
    ) -> Tuple[List[float], List[float]]:
        """
        Evaluate a learning rate schedule.
        
        Args:
            config: Learning rate configuration
            num_steps: Number of steps to evaluate
        
        Returns:
            (learning_rates, losses) tuple
        """
        result = self.adapter.simulate_training(config, num_steps)
        return result.lr_history, result.loss_history


# ==================== Adaptive Optimizer ====================

class AdaptiveOptimizer:
    """
    Adaptive learning rate optimization.
    
    Features:
    - Multiple adaptive algorithms
    - Gradient-based adjustment
    - Learning rate monitoring
    """
    
    def __init__(self):
        self.adapter = LearningRateAdapter()
    
    def create_adaptive_config(
        self,
        name: str,
        optimizer_type: str = "adam",
        initial_lr: float = 0.001,
        warmup_steps: int = 10
    ) -> LearningRateConfig:
        """
        Create an adaptive optimizer configuration.
        
        Args:
            name: Configuration name
            optimizer_type: Type of adaptive optimizer
            initial_lr: Initial learning rate
            warmup_steps: Warmup steps
        
        Returns:
            LearningRateConfig
        """
        from datetime import datetime
        
        config_id = f"lr_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = LearningRateConfig(
            config_id=config_id,
            name=name,
            initial_lr=initial_lr,
            schedule_type="constant",
            schedule_params={},
            optimizer_type=optimizer_type,
            optimizer_params={},
            warmup_steps=warmup_steps,
            warmup_lr=initial_lr * 0.1
        )
        
        return config
    
    def train_with_adaptive_lr(
        self,
        config: LearningRateConfig,
        num_steps: int = 100
    ) -> AdaptationResult:
        """
        Train with adaptive learning rate (simulation).
        
        Args:
            config: Learning rate configuration
            num_steps: Number of training steps
        
        Returns:
            AdaptationResult
        """
        return self.adapter.simulate_training(config, num_steps)


# ==================== Main ====================

def main():
    """Simple demo of Learning Rate Adaptation."""
    print("=" * 70)
    print("📈 Learning Rate Adaptation - Demo")
    print("=" * 70)
    print()
    
    # Create scheduler
    scheduler = LearningRateScheduler()
    
    # Test different schedules
    schedules = {
        "Constant": ("constant", {}),
        "Step Decay": ("step", {"step_size": 30, "gamma": 0.1}),
        "Exponential Decay": ("exponential", {"gamma": 0.99}),
        "Cosine Annealing": ("cosine", {"total_steps": 100, "min_lr": 0.0001}),
        "One-Cycle": ("onecycle", {"total_steps": 100, "max_lr": 0.01, "pct_start": 0.3}),
    }
    
    print("📊 Comparing Learning Rate Schedules")
    print("-" * 70)
    
    results = {}
    for name, (schedule_type, params) in schedules.items():
        config = scheduler.create_config(
            name=name,
            schedule_type=schedule_type,
            schedule_params=params,
            initial_lr=0.001
        )
        
        lr_history, loss_history = scheduler.evaluate_schedule(config, num_steps=100)
        
        results[name] = {
            "lr": lr_history[-1],
            "loss": loss_history[-1],
            "convergence": (loss_history[0] - loss_history[-1]) / loss_history[0]
        }
        
        print(f"  {name}:")
        print(f"    Final LR: {lr_history[-1]:.6f}")
        print(f"    Final Loss: {loss_history[-1]:.3f}")
        print(f"    Convergence: {results[name]['convergence']:.1%}")
        print()
    
    # Find best schedule
    best_name = min(results.keys(), key=lambda x: results[x]["loss"])
    print(f"✅ Best schedule: {best_name} (loss={results[best_name]['loss']:.3f})")
    
    print("\n" + "=" * 70)
    print("✅ Learning Rate Adaptation demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
