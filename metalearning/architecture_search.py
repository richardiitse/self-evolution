#!/usr/bin/env python3
"""
Phase 4: Model Architecture Search

Automatic discovery of optimal model architectures using Neural Architecture Search (NAS).
"""

import sys
import random
import copy
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import json


# ==================== Domain Classes ====================

@dataclass
class ArchitectureConfig:
    """Represents a model architecture configuration."""
    
    config_id: str
    name: str
    layers: List[Dict[str, Any]]  # List of layer configurations
    parameters: Dict[str, Any]  # Model parameters
    performance: float = 0.0  # 0.0 to 1.0
    complexity: float = 0.0  # Model complexity (0.0 to 1.0)
    evaluated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "name": self.name,
            "layers": self.layers,
            "parameters": self.parameters,
            "performance": self.performance,
            "complexity": self.complexity,
            "evaluated": self.evaluated,
            "metadata": self.metadata
        }


@dataclass
class ArchitectureSpace:
    """Defines the searchable architecture space."""
    
    layer_types: List[str]  # Available layer types
    activation_functions: List[str]  # Available activation functions
    layer_sizes: List[int]  # Possible layer sizes
    max_layers: int  # Maximum number of layers
    min_layers: int  # Minimum number of layers
    constraints: Dict[str, Any]  # Search constraints
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_types": self.layer_types,
            "activation_functions": self.activation_functions,
            "layer_sizes": self.layer_sizes,
            "max_layers": self.max_layers,
            "min_layers": self.min_layers,
            "constraints": self.constraints
        }


@dataclass
class EvaluationResult:
    """Result of architecture evaluation."""
    
    config_id: str
    performance: float  # 0.0 to 1.0
    loss: float
    accuracy: float
    training_time: float  # seconds
    inference_time: float  # seconds
    num_parameters: int
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "performance": self.performance,
            "loss": self.loss,
            "accuracy": self.accuracy,
            "training_time": self.training_time,
            "inference_time": self.inference_time,
            "num_parameters": self.num_parameters,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


# ==================== Architecture Search ====================

class ModelArchitectureSearch:
    """
    Neural Architecture Search (NAS) engine.
    
    Features:
    - Architecture space definition
    - NAS algorithms (Random, Bayesian, Evolutionary)
    - Architecture evaluation and ranking
    - Architecture mutation and crossover
    """
    
    def __init__(self, search_space: Optional[ArchitectureSpace] = None):
        self.search_space = search_space if search_space else self._default_search_space()
        
        # Architectures
        self.architectures: Dict[str, ArchitectureConfig] = {}
        self.evaluation_results: Dict[str, EvaluationResult] = {}
        
        # Search state
        self.search_iteration = 0
        self.best_architecture: Optional[str] = None
        self.best_performance = 0.0
    
    def _default_search_space(self) -> ArchitectureSpace:
        """Create default architecture search space."""
        return ArchitectureSpace(
            layer_types=["conv2d", "dense", "maxpool2d", "avgpool2d"],
            activation_functions=["relu", "sigmoid", "tanh"],
            layer_sizes=[64, 128, 256, 512],
            max_layers=10,
            min_layers=2,
            constraints={
                "max_parameters": 10_000_000,
                "max_complexity": 0.8
            }
        )
    
    def generate_config_id(self, name: str) -> str:
        """Generate unique config ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"arch_{timestamp}_{hash(name) % 10000:04d}"
    
    def generate_random_architecture(
        self,
        name: str,
        num_layers: Optional[int] = None
    ) -> ArchitectureConfig:
        """
        Generate a random architecture.
        
        Args:
            name: Architecture name
            num_layers: Number of layers (random if None)
        
        Returns:
            Generated ArchitectureConfig
        """
        if num_layers is None:
            num_layers = random.randint(self.search_space.min_layers, self.search_space.max_layers)
        
        # Generate layers
        layers = []
        for i in range(num_layers):
            layer_type = random.choice(self.search_space.layer_types)
            activation = random.choice(self.search_space.activation_functions)
            size = random.choice(self.search_space.layer_sizes)
            
            layers.append({
                "type": layer_type,
                "activation": activation,
                "size": size
            })
        
        # Calculate complexity
        complexity = len(layers) / self.search_space.max_layers
        
        # Create config
        config_id = self.generate_config_id(name)
        config = ArchitectureConfig(
            config_id=config_id,
            name=name,
            layers=layers,
            parameters={
                "num_layers": num_layers,
                "learning_rate": random.uniform(0.001, 0.01),
                "batch_size": random.choice([32, 64, 128])
            },
            performance=0.0,
            complexity=complexity,
            evaluated=False
        )
        
        return config
    
    def mutate_architecture(
        self,
        config: ArchitectureConfig,
        mutation_rate: float = 0.3
    ) -> ArchitectureConfig:
        """
        Mutate an architecture.
        
        Args:
            config: Architecture to mutate
            mutation_rate: Probability of mutation per layer
        
        Returns:
            Mutated ArchitectureConfig
        """
        new_layers = []
        
        for layer in config.layers:
            new_layer = layer.copy()
            
            if random.random() < mutation_rate:
                # Mutate layer type
                if random.random() < 0.5:
                    new_layer["type"] = random.choice(self.search_space.layer_types)
                
                # Mutate activation
                if random.random() < 0.5:
                    new_layer["activation"] = random.choice(self.search_space.activation_functions)
                
                # Mutate size
                if random.random() < 0.5:
                    new_layer["size"] = random.choice(self.search_space.layer_sizes)
            
            new_layers.append(new_layer)
        
        # Mutate parameters
        new_params = config.parameters.copy()
        if random.random() < 0.3:
            new_params["learning_rate"] = random.uniform(0.001, 0.01)
        if random.random() < 0.3:
            new_params["batch_size"] = random.choice([32, 64, 128])
        
        # Create new config
        new_config = ArchitectureConfig(
            config_id=self.generate_config_id(config.name + "_mut"),
            name=config.name + "_mutated",
            layers=new_layers,
            parameters=new_params,
            performance=0.0,
            complexity=config.complexity,
            evaluated=False
        )
        
        return new_config
    
    def crossover_architectures(
        self,
        parent1: ArchitectureConfig,
        parent2: ArchitectureConfig
    ) -> ArchitectureConfig:
        """
        Crossover two architectures.
        
        Args:
            parent1: First parent architecture
            parent2: Second parent architecture
        
        Returns:
            Child ArchitectureConfig
        """
        # Crossover layers
        child_layers = []
        min_len = min(len(parent1.layers), len(parent2.layers))
        
        for i in range(min_len):
            if random.random() < 0.5:
                child_layers.append(parent1.layers[i].copy())
            else:
                child_layers.append(parent2.layers[i].copy())
        
        # If one parent has more layers, randomly add some
        if len(parent1.layers) > min_len:
            for i in range(min_len, len(parent1.layers)):
                if random.random() < 0.3:
                    child_layers.append(parent1.layers[i].copy())
        elif len(parent2.layers) > min_len:
            for i in range(min_len, len(parent2.layers)):
                if random.random() < 0.3:
                    child_layers.append(parent2.layers[i].copy())
        
        # Ensure minimum layers
        while len(child_layers) < self.search_space.min_layers:
            child_layers.append(parent1.layers[0].copy())
        
        # Crossover parameters
        child_params = {}
        for key in parent1.parameters:
            if random.random() < 0.5:
                child_params[key] = parent1.parameters[key]
            else:
                child_params[key] = parent2.parameters.get(key, parent1.parameters[key])
        
        # Create child config
        child_config = ArchitectureConfig(
            config_id=self.generate_config_id(f"{parent1.name}_{parent2.name}"),
            name=f"{parent1.name}_x_{parent2.name}",
            layers=child_layers,
            parameters=child_params,
            performance=0.0,
            complexity=len(child_layers) / self.search_space.max_layers,
            evaluated=False
        )
        
        return child_config
    
    def evaluate_architecture(
        self,
        config: ArchitectureConfig,
        dataset: str = "dummy"
    ) -> EvaluationResult:
        """
        Evaluate an architecture (simulation).
        
        Args:
            config: Architecture to evaluate
            dataset: Dataset to evaluate on
        
        Returns:
            EvaluationResult
        """
        # Simulate evaluation
        # In reality, this would train and test the model
        
        # Simulated performance based on complexity
        # More complex = potentially better performance
        base_performance = 0.5 + (config.complexity * 0.4)
        
        # Add randomness
        performance = min(1.0, base_performance + random.uniform(-0.1, 0.1))
        
        # Calculate other metrics
        loss = 1.0 - performance + random.uniform(-0.05, 0.05)
        accuracy = performance + random.uniform(-0.02, 0.02)
        
        # Simulated training time (more complex = longer)
        training_time = 100.0 + (config.complexity * 200.0) + random.uniform(-20.0, 20.0)
        
        # Simulated inference time
        inference_time = 10.0 + (config.complexity * 30.0) + random.uniform(-5.0, 5.0)
        
        # Estimate parameters
        num_parameters = int(1_000_000 * (1.0 + config.complexity * 4.0))
        
        # Create result
        result = EvaluationResult(
            config_id=config.config_id,
            performance=performance,
            loss=max(0.0, min(1.0, loss)),
            accuracy=max(0.0, min(1.0, accuracy)),
            training_time=training_time,
            inference_time=inference_time,
            num_parameters=num_parameters,
            metrics={"f1_score": accuracy * 0.95, "precision": accuracy * 0.97}
        )
        
        # Update config
        config.performance = performance
        config.evaluated = True
        
        # Store result
        self.architectures[config.config_id] = config
        self.evaluation_results[config.config_id] = result
        
        # Update best
        if performance > self.best_performance:
            self.best_performance = performance
            self.best_architecture = config.config_id
        
        return result
    
    def random_search(
        self,
        num_iterations: int = 10,
        name_prefix: str = "random"
    ) -> List[EvaluationResult]:
        """
        Perform random architecture search.
        
        Args:
            num_iterations: Number of architectures to search
            name_prefix: Prefix for architecture names
        
        Returns:
            List of evaluation results
        """
        print(f"  🔍 Random search: {num_iterations} iterations")
        
        results = []
        for i in range(num_iterations):
            # Generate architecture
            arch = self.generate_random_architecture(
                name=f"{name_prefix}_{i+1}",
                num_layers=random.randint(
                    self.search_space.min_layers,
                    self.search_space.max_layers
                )
            )
            
            # Evaluate
            result = self.evaluate_architecture(arch)
            results.append(result)
            
            print(f"    Iteration {i+1}/{num_iterations}: {result.performance:.3f}")
        
        # Update search iteration
        self.search_iteration += num_iterations
        
        return results
    
    def evolutionary_search(
        self,
        num_generations: int = 10,
        population_size: int = 10,
        name_prefix: str = "evo"
    ) -> List[EvaluationResult]:
        """
        Perform evolutionary architecture search.
        
        Args:
            num_generations: Number of generations
            population_size: Population size per generation
            name_prefix: Prefix for architecture names
        
        Returns:
            List of evaluation results (final generation)
        """
        print(f"  🧬 Evolutionary search: {num_generations} generations, {population_size} individuals")
        
        # Initialize population
        population = []
        for i in range(population_size):
            arch = self.generate_random_architecture(
                name=f"{name_prefix}_g0_i{i+1}",
                num_layers=random.randint(
                    self.search_space.min_layers,
                    self.search_space.max_layers
                )
            )
            population.append(arch)
        
        # Evolve
        for gen in range(num_generations):
            print(f"    Generation {gen+1}/{num_generations}")
            
            # Evaluate population
            results = []
            for arch in population:
                result = self.evaluate_architecture(arch)
                results.append(result)
            
            # Sort by performance
            population = sorted(population, key=lambda x: -x.performance)
            print(f"      Best: {population[0].performance:.3f}, Avg: {sum(p.performance for p in population)/len(population):.3f}")
            
            # Select top 50%
            survivors = population[:population_size // 2]
            
            # Create new generation through crossover and mutation
            new_population = survivors.copy()
            
            while len(new_population) < population_size:
                # Select parents
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                
                # Crossover or mutate
                if random.random() < 0.5:
                    child = self.crossover_architectures(parent1, parent2)
                else:
                    child = self.mutate_architecture(parent1)
                
                new_population.append(child)
            
            population = new_population
        
        return results
    
    def get_best_architectures(self, n: int = 5) -> List[Tuple[ArchitectureConfig, EvaluationResult]]:
        """
        Get the top N architectures.
        
        Args:
            n: Number of architectures to return
        
        Returns:
            List of (architecture, evaluation) tuples
        """
        # Sort by performance
        sorted_archs = sorted(
            [(arch, self.evaluation_results[arch.config_id]) for arch in self.architectures.values()],
            key=lambda x: -x[1].performance
        )
        
        return sorted_archs[:n]


# ==================== Main ====================

def main():
    """Simple demo of Model Architecture Search."""
    print("=" * 70)
    print("🏗️  Model Architecture Search - Demo")
    print("=" * 70)
    print()
    
    # Create search engine
    search = ModelArchitectureSearch()
    
    # Random search
    print("🔍 Random Search")
    print("-" * 70)
    random_results = search.random_search(num_iterations=10)
    
    # Get best architectures
    print("\n📊 Top 5 Random Architectures")
    print("-" * 70)
    best_random = search.get_best_architectures(n=5)
    for i, (arch, result) in enumerate(best_random):
        print(f"  {i+1}. {arch.name}: {result.performance:.3f} (loss: {result.loss:.3f}, params: {result.num_parameters:,})")
    
    # Evolutionary search
    print("\n🧬 Evolutionary Search")
    print("-" * 70)
    evo_results = search.evolutionary_search(
        num_generations=5,
        population_size=10
    )
    
    # Get best overall
    print("\n📊 Top 5 Overall Architectures")
    print("-" * 70)
    best_overall = search.get_best_architectures(n=5)
    for i, (arch, result) in enumerate(best_overall):
        print(f"  {i+1}. {arch.name}: {result.performance:.3f} (loss: {result.loss:.3f}, params: {result.num_parameters:,})")
    
    print("\n" + "=" * 70)
    print("✅ Model Architecture Search demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
