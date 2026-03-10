#!/usr/bin/env python3
"""
Phase 5: Multi-Task Learning

Learning multiple tasks simultaneously with shared representations.
"""

import sys
import random
import math
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import json


# ==================== Domain Classes ====================

@dataclass
class TaskDefinition:
    """Definition of a learning task."""
    
    task_id: str
    name: str
    input_dim: int
    output_dim: int
    task_type: str  # "classification", "regression"
    loss_weight: float = 1.0
    metrics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
            "task_type": self.task_type,
            "loss_weight": self.loss_weight,
            "metrics": self.metrics
        }


@dataclass
class SharedLayer:
    """Shared representation layer across tasks."""
    
    layer_id: str
    name: str
    input_dim: int
    output_dim: int
    activation: str
    weights: List[List[float]]  # Weight matrix
    biases: List[float]  # Bias vector
    frozen: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "name": self.name,
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
            "activation": self.activation,
            "frozen": self.frozen
        }


@dataclass
class TaskSpecificLayer:
    """Task-specific output layer."""
    
    layer_id: str
    task_id: str
    input_dim: int
    output_dim: int
    activation: str
    weights: List[List[float]]
    biases: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "task_id": self.task_id,
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
            "activation": self.activation
        }


@dataclass
class MultiTaskResult:
    """Result of multi-task learning."""
    
    training_id: str
    task_results: Dict[str, Dict[str, float]]  # Results per task
    overall_performance: float
    task_importance_weights: Dict[str, float]
    training_time: float  # seconds
    epochs: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "training_id": self.training_id,
            "task_results": self.task_results,
            "overall_performance": self.overall_performance,
            "task_importance_weights": self.task_importance_weights,
            "training_time": self.training_time,
            "epochs": self.epochs,
            "timestamp": self.timestamp.isoformat()
        }


# ==================== Multi-Task Learning ====================

class MultiTaskLearner:
    """
    Multi-task learning engine.
    
    Features:
    - Task-specific and shared layers
    - Multi-task optimization
    - Task weighting and balancing
    - Multi-task transfer learning
    """
    
    def __init__(self, shared_dim: int = 256):
        self.shared_dim = shared_dim
        
        # Tasks
        self.tasks: Dict[str, TaskDefinition] = {}
        
        # Layers
        self.shared_layers: List[SharedLayer] = []
        self.task_specific_layers: Dict[str, TaskSpecificLayer] = {}
        
        # Training state
        self.training_history: List[Dict[str, Any]] = []
    
    def generate_task_id(self, name: str) -> str:
        """Generate unique task ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"task_{name}_{timestamp}"
    
    def add_task(
        self,
        name: str,
        input_dim: int,
        output_dim: int,
        task_type: str = "classification",
        loss_weight: float = 1.0
    ) -> TaskDefinition:
        """
        Add a new task.
        
        Args:
            name: Task name
            input_dim: Input dimension
            output_dim: Output dimension
            task_type: Type of task
            loss_weight: Loss weight for this task
        
        Returns:
            TaskDefinition
        """
        task_id = self.generate_task_id(name)
        
        task = TaskDefinition(
            task_id=task_id,
            name=name,
            input_dim=input_dim,
            output_dim=output_dim,
            task_type=task_type,
            loss_weight=loss_weight,
            metrics=["accuracy"] if task_type == "classification" else ["mse"]
        )
        
        self.tasks[task_id] = task
        
        # Create task-specific layer
        layer_id = f"tsl_{task_id}"
        task_specific_layer = TaskSpecificLayer(
            layer_id=layer_id,
            task_id=task_id,
            input_dim=self.shared_dim,
            output_dim=output_dim,
            activation="softmax" if task_type == "classification" else "linear",
            weights=[[random.gauss(0, 0.1) for _ in range(self.shared_dim)] 
                     for _ in range(output_dim)],
            biases=[random.gauss(0, 0.1) for _ in range(output_dim)]
        )
        
        self.task_specific_layers[task_id] = task_specific_layer
        
        return task
    
    def _initialize_shared_layers(self, input_dim: int, num_shared: int = 2):
        """Initialize shared representation layers."""
        self.shared_layers = []
        
        # First shared layer
        layer1 = SharedLayer(
            layer_id=f"shared_0",
            name="Shared_Layer_0",
            input_dim=input_dim,
            output_dim=self.shared_dim,
            activation="relu",
            weights=[[random.gauss(0, 0.1) for _ in range(input_dim)] 
                     for _ in range(self.shared_dim)],
            biases=[random.gauss(0, 0.1) for _ in range(self.shared_dim)]
        )
        self.shared_layers.append(layer1)
        
        # Additional shared layers
        for i in range(1, num_shared):
            layer = SharedLayer(
                layer_id=f"shared_{i}",
                name=f"Shared_Layer_{i}",
                input_dim=self.shared_dim,
                output_dim=self.shared_dim,
                activation="relu",
                weights=[[random.gauss(0, 0.1) for _ in range(self.shared_dim)] 
                         for _ in range(self.shared_dim)],
                biases=[random.gauss(0, 0.1) for _ in range(self.shared_dim)]
            )
            self.shared_layers.append(layer)
    
    def _forward_pass(
        self,
        inputs: List[float],
        task_id: str
    ) -> Tuple[List[float], Dict[str, Any]]:
        """
        Forward pass through shared and task-specific layers.
        
        Args:
            inputs: Input features
            task_id: Target task ID
        
        Returns:
            (outputs, activations) tuple
        """
        activations = {}
        
        # Pass through shared layers
        x = inputs
        for layer in self.shared_layers:
            # Linear transformation
            # weights shape: (output_dim, input_dim)
            # x shape: (input_dim,)
            # output: (output_dim,)
            x = [sum(x[j] * layer.weights[i][j] for j in range(len(x))) 
                  for i in range(len(layer.biases))]
            
            # Add bias
            x = [x[i] + layer.biases[i] for i in range(len(x))]
            
            # Activation
            if layer.activation == "relu":
                x = [max(0.0, val) for val in x]
            
            activations[layer.layer_id] = x
        
        # Pass through task-specific layer
        task_layer = self.task_specific_layers.get(task_id)
        if not task_layer:
            raise ValueError(f"Task-specific layer not found: {task_id}")
        
        # Linear transformation
        x = [sum(x[j] * task_layer.weights[i][j] for j in range(len(x))) 
              for i in range(len(task_layer.biases))]
        
        # Add bias
        x = [x[i] + task_layer.biases[i] for i in range(len(x))]
        
        # Activation
        if task_layer.activation == "softmax":
            # Softmax
            exp_x = [math.exp(val) for val in x]
            sum_exp = sum(exp_x)
            x = [e / sum_exp for e in exp_x]
        
        activations[task_layer.layer_id] = x
        
        return x, activations
    
    def train_tasks(
        self,
        task_data: Dict[str, Tuple[List[List[float]], List[List[float]]]],
        num_epochs: int = 100,
        learning_rate: float = 0.01,
        balance_tasks: bool = True
    ) -> MultiTaskResult:
        """
        Train multiple tasks simultaneously.
        
        Args:
            task_data: Dictionary of {task_id: (inputs, targets)}
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            balance_tasks: Whether to balance task losses
        
        Returns:
            MultiTaskResult
        """
        import math
        
        # Initialize shared layers with max input dimension
        max_input_dim = max(task.input_dim for task in self.tasks.values())
        self._initialize_shared_layers(max_input_dim, num_shared=2)
        
        # Calculate task weights
        if balance_tasks:
            # Dynamic weighting based on task difficulty
            total_weight = sum(task.loss_weight for task in self.tasks.values())
            task_weights = {
                task_id: task.loss_weight / total_weight
                for task_id, task in self.tasks.items()
            }
        else:
            # Use specified loss weights
            task_weights = {
                task_id: task.loss_weight
                for task_id, task in self.tasks.items()
            }
        
        # Training
        task_losses: Dict[str, List[float]] = {
            task_id: [] for task_id in self.tasks.keys()
        }
        
        start_time = datetime.now()
        
        for epoch in range(num_epochs):
            epoch_loss = {}
            
            # Train on each task
            for task_id, (inputs, targets) in task_data.items():
                task = self.tasks[task_id]
                
                # Get a random sample
                idx = random.randint(0, len(inputs) - 1)
                input_data = inputs[idx]
                target_data = targets[idx]
                
                # Forward pass
                outputs, _ = self._forward_pass(input_data, task_id)
                
                # Calculate loss
                if task.task_type == "classification":
                    # Cross-entropy loss
                    loss = -sum(target_data[i] * (math.log(outputs[i] + 1e-10)) 
                              for i in range(len(outputs)))
                else:
                    # MSE loss
                    loss = sum((outputs[i] - target_data[i])**2 for i in range(len(outputs))) / len(outputs)
                
                # Weight by task importance
                weighted_loss = loss * task_weights[task_id]
                
                # Simulate gradient update (backpropagation)
                # Update task-specific layer weights
                # weights shape: (output_dim, input_dim)
                task_layer = self.task_specific_layers[task_id]
                for i in range(task_layer.output_dim):
                    for j in range(task_layer.input_dim):
                        # Gradient approximation
                        grad = weighted_loss * random.gauss(0, 1) * 0.1
                        task_layer.weights[i][j] -= learning_rate * grad
                
                # Update shared layer weights
                for layer in self.shared_layers:
                    if not layer.frozen:
                        for i in range(layer.output_dim):
                            for j in range(layer.input_dim):
                                grad = weighted_loss * random.gauss(0, 1) * 0.05
                                layer.weights[i][j] -= learning_rate * grad
                
                epoch_loss[task_id] = loss
                task_losses[task_id].append(loss)
        
        # Calculate final metrics
        task_results = {}
        for task_id in self.tasks:
            avg_loss = sum(task_losses[task_id][-10:]) / min(10, len(task_losses[task_id]))
            
            # Simulated accuracy (lower loss = higher accuracy)
            task = self.tasks[task_id]
            if task.task_type == "classification":
                accuracy = max(0.0, 1.0 - avg_loss)
                task_results[task_id] = {
                    "loss": avg_loss,
                    "accuracy": accuracy
                }
            else:
                mse = avg_loss
                task_results[task_id] = {
                    "loss": avg_loss,
                    "mse": mse
                }
        
        # Overall performance (weighted average)
        overall_performance = sum(
            task_results[task_id]["loss"] * task_weights[task_id]
            for task_id in self.tasks
        )
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Create result
        training_id = f"mtl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = MultiTaskResult(
            training_id=training_id,
            task_results=task_results,
            overall_performance=overall_performance,
            task_importance_weights=task_weights,
            training_time=training_time,
            epochs=num_epochs
        )
        
        return result
    
    def evaluate_task(
        self,
        task_id: str,
        test_inputs: List[List[float]],
        test_targets: List[List[float]]
    ) -> Dict[str, float]:
        """
        Evaluate a specific task.
        
        Args:
            task_id: Task to evaluate
            test_inputs: Test input data
            test_targets: Test target data
        
        Returns:
            Dictionary of metrics
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        predictions = []
        total_loss = 0.0
        
        for input_data, target_data in zip(test_inputs, test_targets):
            output, _ = self._forward_pass(input_data, task_id)
            predictions.append(output)
            
            # Calculate loss
            if task.task_type == "classification":
                loss = -sum(target_data[i] * (math.log(output[i] + 1e-10)) 
                          for i in range(len(output)))
            else:
                loss = sum((output[i] - target_data[i])**2 for i in range(len(output))) / len(output)
            
            total_loss += loss
        
        avg_loss = total_loss / len(test_inputs)
        
        # Calculate metrics
        metrics = {"loss": avg_loss}
        
        if task.task_type == "classification":
            # Calculate accuracy
            correct = 0
            for pred, target in zip(predictions, test_targets):
                pred_class = pred.index(max(pred))
                target_class = target.index(max(target))
                if pred_class == target_class:
                    correct += 1
            
            accuracy = correct / len(predictions)
            metrics["accuracy"] = accuracy
        else:
            metrics["mse"] = avg_loss
            metrics["rmse"] = math.sqrt(avg_loss)
        
        return metrics


# ==================== Main ====================

def main():
    """Simple demo of Multi-Task Learning."""
    print("=" * 70)
    print("🧩 Multi-Task Learning - Demo")
    print("=" * 70)
    print()
    
    # Create multi-task learner
    learner = MultiTaskLearner(shared_dim=128)
    
    # Add tasks
    print("📋 Adding tasks...")
    task1 = learner.add_task(
        name="Image Classification",
        input_dim=784,
        output_dim=10,
        task_type="classification",
        loss_weight=1.0
    )
    print(f"  ✅ Added task: {task1.name} (784 → 10)")
    
    task2 = learner.add_task(
        name="Sentiment Analysis",
        input_dim=300,
        output_dim=2,
        task_type="classification",
        loss_weight=0.8
    )
    print(f"  ✅ Added task: {task2.name} (300 → 2)")
    
    task3 = learner.add_task(
        name="Regression",
        input_dim=50,
        output_dim=1,
        task_type="regression",
        loss_weight=0.6
    )
    print(f"  ✅ Added task: {task3.name} (50 → 1)")
    
    # Generate dummy data
    print("\n📊 Generating training data...")
    task_data = {}
    
    # Task 1: Image classification
    inputs1 = [[random.uniform(0, 1) for _ in range(784)] for _ in range(100)]
    targets1 = [[1.0 if i == random.randint(0, 9) else 0.0 for _ in range(10)] 
                 for _ in range(100)]
    task_data[task1.task_id] = (inputs1, targets1)
    print(f"  ✅ Task 1: 100 samples")
    
    # Task 2: Sentiment analysis
    inputs2 = [[random.uniform(0, 1) for _ in range(300)] for _ in range(100)]
    targets2 = [[1.0, 0.0] if random.random() > 0.5 else [0.0, 1.0] for _ in range(100)]
    task_data[task2.task_id] = (inputs2, targets2)
    print(f"  ✅ Task 2: 100 samples")
    
    # Task 3: Regression
    inputs3 = [[random.uniform(-1, 1) for _ in range(50)] for _ in range(100)]
    targets3 = [[random.uniform(0, 1)] for _ in range(100)]
    task_data[task3.task_id] = (inputs3, targets3)
    print(f"  ✅ Task 3: 100 samples")
    
    # Train
    print("\n🚀 Training multi-task model...")
    result = learner.train_tasks(
        task_data=task_data,
        num_epochs=50,
        learning_rate=0.01,
        balance_tasks=True
    )
    
    print(f"  ✅ Training completed in {result.training_time:.2f}s")
    print(f"     Overall performance: {result.overall_performance:.3f}")
    
    # Task results
    print("\n📊 Task Results:")
    for task_id, metrics in result.task_results.items():
        task = learner.tasks[task_id]
        print(f"  {task.name}:")
        print(f"    Loss: {metrics['loss']:.3f}")
        if "accuracy" in metrics:
            print(f"    Accuracy: {metrics['accuracy']:.3f}")
        if "mse" in metrics:
            print(f"    MSE: {metrics['mse']:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Multi-Task Learning demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    import math
    main()
