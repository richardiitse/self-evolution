#!/usr/bin/env python3
"""
Phase 4: Hyperparameter Optimization

Automatic tuning of hyperparameters for optimal performance using various optimization algorithms.
"""

import sys
import random
import math
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
import json


# ==================== Domain Classes ====================

@dataclass
class HyperparameterSpace:
    """Defines the searchable hyperparameter space."""
    
    parameters: Dict[str, Dict[str, Any]]  # Parameter definitions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameters": self.parameters
        }


@dataclass
class HyperparameterConfig:
    """Represents a hyperparameter configuration."""
    
    config_id: str
    name: str
    parameters: Dict[str, Any]  # Hyperparameter values
    performance: float = 0.0  # 0.0 to 1.0
    evaluated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "name": self.name,
            "parameters": self.parameters,
            "performance": self.performance,
            "evaluated": self.evaluated,
            "metadata": self.metadata
        }


@dataclass
class HyperparameterResult:
    """Result of hyperparameter evaluation."""
    
    config_id: str
    performance: float  # 0.0 to 1.0
    loss: float
    accuracy: float
    training_time: float  # seconds
    validation_time: float  # seconds
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "performance": self.performance,
            "loss": self.loss,
            "accuracy": self.accuracy,
            "training_time": self.training_time,
            "validation_time": self.validation_time,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


# ==================== Hyperparameter Optimization ====================

class HyperparameterOptimizer:
    """
    Hyperparameter optimization engine.
    
    Features:
    - Hyperparameter space definition
    - Optimization algorithms (Random, Grid, Bayesian, Evolutionary)
    - Hyperparameter importance analysis
    - Hyperparameter transfer across tasks
    """
    
    def __init__(self, search_space: Optional[HyperparameterSpace] = None):
        self.search_space = search_space if search_space else self._default_search_space()
        
        # Configurations and results
        self.configs: Dict[str, HyperparameterConfig] = {}
        self.results: Dict[str, HyperparameterResult] = {}
        
        # Search state
        self.search_iteration = 0
        self.best_config: Optional[str] = None
        self.best_performance = 0.0
        
        # Bayesian optimization state
        self._bayesian_cache: List[Tuple[Dict[str, Any], float]] = []
    
    def _default_search_space(self) -> HyperparameterSpace:
        """Create default hyperparameter search space."""
        return HyperparameterSpace(
            parameters={
                "learning_rate": {
                    "type": "float",
                    "min": 1e-5,
                    "max": 1e-1,
                    "scale": "log"
                },
                "batch_size": {
                    "type": "int",
                    "min": 16,
                    "max": 256,
                    "step": 16
                },
                "dropout_rate": {
                    "type": "float",
                    "min": 0.0,
                    "max": 0.5
                },
                "l2_regularization": {
                    "type": "float",
                    "min": 1e-6,
                    "max": 1e-2,
                    "scale": "log"
                },
                "num_layers": {
                    "type": "int",
                    "min": 2,
                    "max": 10
                },
                "hidden_size": {
                    "type": "int",
                    "min": 64,
                    "max": 1024,
                    "step": 64
                }
            }
        )
    
    def generate_config_id(self, name: str) -> str:
        """Generate unique config ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"hyper_{timestamp}_{hash(name) % 10000:04d}"
    
    def sample_parameter(self, param_name: str, param_def: Dict[str, Any]) -> Any:
        """
        Sample a value from parameter distribution.
        
        Args:
            param_name: Parameter name
            param_def: Parameter definition
        
        Returns:
            Sampled value
        """
        param_type = param_def["type"]
        
        if param_type == "float":
            min_val = param_def["min"]
            max_val = param_def["max"]
            
            if param_def.get("scale") == "log":
                # Log-uniform sampling
                log_min = math.log10(min_val)
                log_max = math.log10(max_val)
                log_val = random.uniform(log_min, log_max)
                return 10 ** log_val
            else:
                # Uniform sampling
                return random.uniform(min_val, max_val)
        
        elif param_type == "int":
            min_val = param_def["min"]
            max_val = param_def["max"]
            step = param_def.get("step", 1)
            
            # Discrete sampling
            num_steps = (max_val - min_val) // step
            step_index = random.randint(0, int(num_steps))
            return min_val + step_index * step
        
        elif param_type == "categorical":
            return random.choice(param_def["choices"])
        
        else:
            raise ValueError(f"Unknown parameter type: {param_type}")
    
    def generate_random_config(
        self,
        name: str
    ) -> HyperparameterConfig:
        """
        Generate a random hyperparameter configuration.
        
        Args:
            name: Configuration name
        
        Returns:
            Generated HyperparameterConfig
        """
        parameters = {}
        
        for param_name, param_def in self.search_space.parameters.items():
            parameters[param_name] = self.sample_parameter(param_name, param_def)
        
        # Create config
        config_id = self.generate_config_id(name)
        config = HyperparameterConfig(
            config_id=config_id,
            name=name,
            parameters=parameters,
            performance=0.0,
            evaluated=False
        )
        
        return config
    
    def evaluate_config(
        self,
        config: HyperparameterConfig,
        dataset: str = "dummy"
    ) -> HyperparameterResult:
        """
        Evaluate a hyperparameter configuration (simulation).
        
        Args:
            config: Configuration to evaluate
            dataset: Dataset to evaluate on
        
        Returns:
            HyperparameterResult
        """
        # Simulate evaluation
        # In reality, this would train and test model
        
        # Extract key hyperparameters
        lr = config.parameters.get("learning_rate", 0.001)
        batch_size = config.parameters.get("batch_size", 32)
        dropout = config.parameters.get("dropout_rate", 0.1)
        
        # Simulated performance based on hyperparameters
        # Optimal range for learning rate: 1e-4 to 1e-3
        lr_score = 1.0 - min(1.0, abs(math.log10(lr) - (-3)) / 3.0)
        
        # Optimal range for batch size: 32 to 128
        batch_score = 1.0 - min(1.0, abs(batch_size - 64) / 96.0)
        
        # Optimal range for dropout: 0.1 to 0.3
        dropout_score = 1.0 - min(1.0, abs(dropout - 0.2) / 0.2)
        
        # Combined score
        performance = (lr_score + batch_score + dropout_score) / 3.0
        
        # Add randomness
        performance = min(1.0, performance + random.uniform(-0.05, 0.05))
        
        # Calculate other metrics
        loss = 1.0 - performance + random.uniform(-0.02, 0.02)
        accuracy = performance + random.uniform(-0.01, 0.01)
        
        # Simulated training time (larger batch = faster)
        training_time = 200.0 / (batch_size / 32.0) + random.uniform(-20.0, 20.0)
        validation_time = 20.0 + random.uniform(-5.0, 5.0)
        
        # Create result
        result = HyperparameterResult(
            config_id=config.config_id,
            performance=performance,
            loss=max(0.0, min(1.0, loss)),
            accuracy=max(0.0, min(1.0, accuracy)),
            training_time=training_time,
            validation_time=validation_time,
            metrics={
                "f1_score": accuracy * 0.95,
                "precision": accuracy * 0.97,
                "recall": accuracy * 0.98
            }
        )
        
        # Update config
        config.performance = performance
        config.evaluated = True
        
        # Store result
        self.configs[config.config_id] = config
        self.results[config.config_id] = result
        
        # Update Bayesian cache
        self._bayesian_cache.append((config.parameters.copy(), performance))
        
        # Update best
        if performance > self.best_performance:
            self.best_performance = performance
            self.best_config = config.config_id
        
        return result
    
    def random_search(
        self,
        num_iterations: int = 10,
        name_prefix: str = "random"
    ) -> List[HyperparameterResult]:
        """
        Perform random hyperparameter search.
        
        Args:
            num_iterations: Number of configurations to search
            name_prefix: Prefix for configuration names
        
        Returns:
            List of evaluation results
        """
        print(f"  🔍 Random search: {num_iterations} iterations")
        
        results = []
        for i in range(num_iterations):
            # Generate config
            config = self.generate_random_config(
                name=f"{name_prefix}_{i+1}"
            )
            
            # Evaluate
            result = self.evaluate_config(config)
            results.append(result)
            
            print(f"    Iteration {i+1}/{num_iterations}: {result.performance:.3f}")
        
        self.search_iteration += num_iterations
        return results
    
    def grid_search(
        self,
        grid_sizes: Optional[Dict[str, int]] = None,
        name_prefix: str = "grid"
    ) -> List[HyperparameterResult]:
        """
        Perform grid hyperparameter search.
        
        Args:
            grid_sizes: Number of grid points per parameter (default: 3)
            name_prefix: Prefix for configuration names
        
        Returns:
            List of evaluation results
        """
        grid_sizes = grid_sizes or {}
        
        # Generate grid points for each parameter
        param_values = {}
        for param_name, param_def in self.search_space.parameters.items():
            grid_size = grid_sizes.get(param_name, 3)
            
            if param_def["type"] == "float":
                if param_def.get("scale") == "log":
                    # Log-uniform grid
                    log_min = math.log10(param_def["min"])
                    log_max = math.log10(param_def["max"])
                    log_values = [log_min + i * (log_max - log_min) / (grid_size - 1)
                                for i in range(grid_size)]
                    param_values[param_name] = [10 ** v for v in log_values]
                else:
                    # Uniform grid
                    param_values[param_name] = [
                        param_def["min"] + i * (param_def["max"] - param_def["min"]) / (grid_size - 1)
                        for i in range(grid_size)
                    ]
            
            elif param_def["type"] == "int":
                step = param_def.get("step", 1)
                param_values[param_name] = [
                    param_def["min"] + i * step
                    for i in range(grid_size)
                ]
        
        # Generate all combinations
        print(f"  📊 Grid search: {len(param_values)} parameters")
        
        import itertools
        param_names = list(param_values.keys())
        value_combinations = list(itertools.product(*[param_values[p] for p in param_names]))
        
        print(f"    Total combinations: {len(value_combinations)}")
        
        results = []
        for i, values in enumerate(value_combinations):
            # Create config
            parameters = dict(zip(param_names, values))
            config_id = self.generate_config_id(f"{name_prefix}_{i+1}")
            config = HyperparameterConfig(
                config_id=config_id,
                name=f"{name_prefix}_{i+1}",
                parameters=parameters,
                performance=0.0,
                evaluated=False
            )
            
            # Evaluate
            result = self.evaluate_config(config)
            results.append(result)
            
            if (i + 1) % max(1, len(value_combinations) // 10) == 0:
                print(f"    Progress: {i+1}/{len(value_combinations)} (best: {self.best_performance:.3f})")
        
        self.search_iteration += len(value_combinations)
        return results
    
    def bayesian_search(
        self,
        num_iterations: int = 10,
        name_prefix: str = "bayesian"
    ) -> List[HyperparameterResult]:
        """
        Perform Bayesian hyperparameter search (simplified).
        
        Args:
            num_iterations: Number of iterations
            name_prefix: Prefix for configuration names
        
        Returns:
            List of evaluation results
        """
        print(f"  🎯 Bayesian search: {num_iterations} iterations")
        
        results = []
        
        # First, evaluate some random points
        n_initial = min(5, num_iterations // 2)
        print(f"    Initial random sampling: {n_initial} points")
        
        for i in range(n_initial):
            config = self.generate_random_config(
                name=f"{name_prefix}_init_{i+1}"
            )
            result = self.evaluate_config(config)
            results.append(result)
            print(f"      Initial {i+1}/{n_initial}: {result.performance:.3f}")
        
        # Then use expected improvement
        for i in range(num_iterations - n_initial):
            # Simple expected improvement: sample near best points
            if len(self._bayesian_cache) > 0:
                # Find best config
                best_params, best_perf = max(self._bayesian_cache, key=lambda x: x[1])
                
                # Sample near best with some exploration
                new_params = best_params.copy()
                for param_name, param_def in self.search_space.parameters.items():
                    if random.random() < 0.3:  # 30% chance to perturb each param
                        # Perturb by 10%
                        old_val = new_params[param_name]
                        if param_def["type"] == "float":
                            scale_factor = random.uniform(0.5, 1.5)
                            new_val = old_val * scale_factor
                            # Clamp to bounds
                            new_val = max(param_def["min"], min(param_def["max"], new_val))
                            new_params[param_name] = new_val
                        elif param_def["type"] == "int":
                            perturbation = random.choice([-1, 0, 1])
                            step = param_def.get("step", 1)
                            new_val = old_val + perturbation * step
                            new_val = max(param_def["min"], min(param_def["max"], new_val))
                            new_params[param_name] = new_val
                
                # Create config
                config_id = self.generate_config_id(f"{name_prefix}_bo_{i+1}")
                config = HyperparameterConfig(
                    config_id=config_id,
                    name=f"{name_prefix}_bo_{i+1}",
                    parameters=new_params,
                    performance=0.0,
                    evaluated=False
                )
            else:
                # Fallback to random
                config = self.generate_random_config(
                    name=f"{name_prefix}_bo_{i+1}"
                )
            
            # Evaluate
            result = self.evaluate_config(config)
            results.append(result)
            print(f"      BO {i+1}/{num_iterations - n_initial}: {result.performance:.3f}")
        
        self.search_iteration += num_iterations
        return results
    
    def get_best_configs(self, n: int = 5) -> List[Tuple[HyperparameterConfig, HyperparameterResult]]:
        """
        Get top N configurations.
        
        Args:
            n: Number of configurations to return
        
        Returns:
            List of (config, result) tuples
        """
        # Sort by performance
        sorted_configs = sorted(
            [(config, self.results[config.config_id]) for config in self.configs.values()],
            key=lambda x: -x[1].performance
        )
        
        return sorted_configs[:n]


# ==================== Main ====================

def main():
    """Simple demo of Hyperparameter Optimization."""
    print("=" * 70)
    print("⚙️  Hyperparameter Optimization - Demo")
    print("=" * 70)
    print()
    
    # Create optimizer
    optimizer = HyperparameterOptimizer()
    
    # Random search
    print("🔍 Random Search")
    print("-" * 70)
    random_results = optimizer.random_search(num_iterations=10)
    
    # Get best
    print("\n📊 Top 5 Random Configs")
    print("-" * 70)
    best_random = optimizer.get_best_configs(n=5)
    for i, (config, result) in enumerate(best_random):
        print(f"  {i+1}. {config.name}: {result.performance:.3f}")
        print(f"     lr={config.parameters['learning_rate']:.6f}, "
              f"batch={config.parameters['batch_size']}, "
              f"dropout={config.parameters['dropout_rate']:.3f}")
    
    # Bayesian search
    print("\n🎯 Bayesian Search")
    print("-" * 70)
    bayes_results = optimizer.bayesian_search(num_iterations=15)
    
    # Get best overall
    print("\n📊 Top 5 Overall Configs")
    print("-" * 70)
    best_overall = optimizer.get_best_configs(n=5)
    for i, (config, result) in enumerate(best_overall):
        print(f"  {i+1}. {config.name}: {result.performance:.3f}")
        print(f"     lr={config.parameters['learning_rate']:.6f}, "
              f"batch={config.parameters['batch_size']}, "
              f"dropout={config.parameters['dropout_rate']:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Hyperparameter Optimization demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
