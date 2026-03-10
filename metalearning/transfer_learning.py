#!/usr/bin/env python3
"""
Phase 4: Transfer Learning Integration

Integration of transfer learning across skills and tasks.
"""

import sys
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import json


# ==================== Domain Classes ====================

@dataclass
class PretrainedModel:
    """Represents a pretrained model."""
    
    model_id: str
    name: str
    task_type: str  # "classification", "regression", etc.
    architecture: str  # "cnn", "transformer", etc.
    source: str  # Where it came from
    accuracy: float  # Performance on source task
    num_parameters: int
    features_dim: int
    training_data: str  # What data it was trained on
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "task_type": self.task_type,
            "architecture": self.architecture,
            "source": self.source,
            "accuracy": self.accuracy,
            "num_parameters": self.num_parameters,
            "features_dim": self.features_dim,
            "training_data": self.training_data,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class FeatureExtraction:
    """Extracted features from a model."""
    
    extraction_id: str
    model_id: str
    features: List[float]  # Feature vector
    layer: str  # Which layer extracted from
    input_id: str  # ID of input
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "extraction_id": self.extraction_id,
            "model_id": self.model_id,
            "features": self.features[:10],  # First 10 for storage
            "features_dim": len(self.features),
            "layer": self.layer,
            "input_id": self.input_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning a model."""
    
    config_id: str
    model_id: str
    target_task: str
    freeze_layers: List[str]  # Which layers to freeze
    learning_rate: float
    epochs: int
    batch_size: int
    optimizer: str
    loss_function: str
    metrics: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "model_id": self.model_id,
            "target_task": self.target_task,
            "freeze_layers": self.freeze_layers,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "optimizer": self.optimizer,
            "loss_function": self.loss_function,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TransferResult:
    """Result of transfer learning."""
    
    transfer_id: str
    config_id: str
    model_id: str
    target_task: str
    performance: float  # 0.0 to 1.0
    accuracy: float
    loss: float
    training_time: float  # seconds
    convergence_rate: float
    final_lr: float
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transfer_id": self.transfer_id,
            "config_id": self.config_id,
            "model_id": self.model_id,
            "target_task": self.target_task,
            "performance": self.performance,
            "accuracy": self.accuracy,
            "loss": self.loss,
            "training_time": self.training_time,
            "convergence_rate": self.convergence_rate,
            "final_lr": self.final_lr,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


# ==================== Transfer Learning Integration ====================

class TransferLearningIntegrator:
    """
    Orchestrates transfer learning across skills and tasks.
    
    Features:
    - Pretrained model selection
    - Feature extraction and storage
    - Fine-tuning strategies
    - Domain adaptation
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".transfer_learning"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Models and features
        self.models: Dict[str, PretrainedModel] = {}
        self.features: Dict[str, FeatureExtraction] = {}
        self.transfer_results: Dict[str, TransferResult] = {}
        
        # Initialize with some default models
        self._init_default_models()
    
    def _init_default_models(self):
        """Initialize with default pretrained models."""
        # Image classification model
        image_model = PretrainedModel(
            model_id="resnet50_imagenet",
            name="ResNet-50 (ImageNet)",
            task_type="classification",
            architecture="cnn",
            source="imagenet",
            accuracy=0.76,
            num_parameters=25_600_000,
            features_dim=2048,
            training_data="ImageNet",
            created_at=datetime.now()
        )
        self.models[image_model.model_id] = image_model
        
        # Text classification model
        text_model = PretrainedModel(
            model_id="bert_base_uncased",
            name="BERT-Base (Uncased)",
            task_type="classification",
            architecture="transformer",
            source="wikipedia",
            accuracy=0.89,
            num_parameters=110_000_000,
            features_dim=768,
            training_data="Wikipedia",
            created_at=datetime.now()
        )
        self.models[text_model.model_id] = text_model
        
        # Regression model
        regression_model = PretrainedModel(
            model_id="mlp_regression",
            name="MLP Regressor",
            task_type="regression",
            architecture="mlp",
            source="synthetic",
            accuracy=0.85,
            num_parameters=1_000_000,
            features_dim=512,
            training_data="Synthetic data",
            created_at=datetime.now()
        )
        self.models[regression_model.model_id] = regression_model
    
    def generate_model_id(self, name: str) -> str:
        """Generate unique model ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"model_{timestamp}_{hash(name) % 10000:04d}"
    
    def register_model(
        self,
        name: str,
        task_type: str,
        architecture: str,
        source: str,
        accuracy: float,
        num_parameters: int,
        features_dim: int,
        training_data: str
    ) -> PretrainedModel:
        """
        Register a new pretrained model.
        
        Args:
            name: Model name
            task_type: Type of task
            architecture: Model architecture
            source: Where model came from
            accuracy: Accuracy on source task
            num_parameters: Number of parameters
            features_dim: Dimension of feature space
            training_data: Training data description
        
        Returns:
            PretrainedModel
        """
        model_id = self.generate_model_id(name)
        
        model = PretrainedModel(
            model_id=model_id,
            name=name,
            task_type=task_type,
            architecture=architecture,
            source=source,
            accuracy=accuracy,
            num_parameters=num_parameters,
            features_dim=features_dim,
            training_data=training_data,
            created_at=datetime.now()
        )
        
        self.models[model_id] = model
        return model
    
    def select_model(
        self,
        target_task: str,
        preferred_architecture: Optional[str] = None,
        min_accuracy: Optional[float] = None,
        max_parameters: Optional[int] = None
    ) -> Optional[PretrainedModel]:
        """
        Select best pretrained model for target task.
        
        Args:
            target_task: Target task type
            preferred_architecture: Preferred architecture
            min_accuracy: Minimum accuracy threshold
            max_parameters: Maximum number of parameters
        
        Returns:
            Selected PretrainedModel or None
        """
        candidates = list(self.models.values())
        
        # Filter by task type
        candidates = [m for m in candidates if m.task_type == target_task or target_task == "any"]
        
        # Filter by architecture
        if preferred_architecture:
            candidates = [m for m in candidates if m.architecture == preferred_architecture]
        
        # Filter by accuracy
        if min_accuracy:
            candidates = [m for m in candidates if m.accuracy >= min_accuracy]
        
        # Filter by parameters
        if max_parameters:
            candidates = [m for m in candidates if m.num_parameters <= max_parameters]
        
        if not candidates:
            return None
        
        # Return best by accuracy
        return max(candidates, key=lambda x: x.accuracy)
    
    def extract_features(
        self,
        model_id: str,
        input_id: str,
        layer: str = "last_hidden"
    ) -> FeatureExtraction:
        """
        Extract features from a model (simulation).
        
        Args:
            model_id: Model ID
            input_id: Input identifier
            layer: Which layer to extract from
        
        Returns:
            FeatureExtraction
        """
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        # Simulate feature extraction
        # In reality, this would run the model and extract features
        features_dim = model.features_dim
        features = [random.gauss(0, 1) for _ in range(features_dim)]
        
        # Normalize
        norm = sum(f**2 for f in features) ** 0.5
        if norm > 0:
            features = [f / norm for f in features]
        
        extraction_id = f"feat_{model_id}_{input_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        extraction = FeatureExtraction(
            extraction_id=extraction_id,
            model_id=model_id,
            features=features,
            layer=layer,
            input_id=input_id
        )
        
        self.features[extraction_id] = extraction
        return extraction
    
    def create_finetuning_config(
        self,
        model_id: str,
        target_task: str,
        learning_rate: float = 0.001,
        epochs: int = 10,
        batch_size: int = 32,
        optimizer: str = "adam",
        freeze_layers: Optional[List[str]] = None
    ) -> FineTuningConfig:
        """
        Create a fine-tuning configuration.
        
        Args:
            model_id: Model ID to fine-tune
            target_task: Target task
            learning_rate: Learning rate
            epochs: Number of epochs
            batch_size: Batch size
            optimizer: Optimizer type
            freeze_layers: Layers to freeze
        
        Returns:
            FineTuningConfig
        """
        config_id = f"ft_{model_id}_{target_task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        freeze_layers = freeze_layers or ["conv1", "conv2", "conv3"]  # Default freeze
        
        config = FineTuningConfig(
            config_id=config_id,
            model_id=model_id,
            target_task=target_task,
            freeze_layers=freeze_layers,
            learning_rate=learning_rate,
            epochs=epochs,
            batch_size=batch_size,
            optimizer=optimizer,
            loss_function="cross_entropy",
            metrics=["accuracy", "f1"]
        )
        
        return config
    
    def fine_tune_model(
        self,
        config: FineTuningConfig,
        target_data_size: int = 1000
    ) -> TransferResult:
        """
        Fine-tune a model on target task (simulation).
        
        Args:
            config: Fine-tuning configuration
            target_data_size: Size of target dataset
        
        Returns:
            TransferResult
        """
        model = self.models.get(config.model_id)
        if not model:
            raise ValueError(f"Model not found: {config.model_id}")
        
        # Simulate fine-tuning
        # Performance depends on:
        # - Model's original accuracy (higher = better transfer)
        # - Learning rate (optimal around 0.001)
        # - Data size (more = better, but diminishing returns)
        # - Frozen layers (more frozen = less overfitting but slower learning)
        
        # Optimal LR
        optimal_lr = 0.001
        lr_penalty = abs(config.learning_rate - optimal_lr) / optimal_lr
        
        # Data size factor
        data_factor = min(1.0, target_data_size / 5000.0)
        
        # Frozen layers factor
        frozen_factor = min(1.0, len(config.freeze_layers) / 10.0)
        
        # Calculate performance
        base_performance = model.accuracy * 0.9  # Transfer penalty
        performance = base_performance * (1.0 - lr_penalty * 0.2) * data_factor * (1.0 + frozen_factor * 0.1)
        
        # Add randomness
        performance = min(1.0, performance + random.uniform(-0.05, 0.05))
        
        # Calculate other metrics
        accuracy = performance
        loss = 1.0 - performance + random.uniform(-0.02, 0.02)
        
        # Training time
        epochs_per_step = target_data_size / config.batch_size
        training_time = epochs_per_step * config.epochs * 0.1  # 0.1 seconds per step
        
        # Convergence rate
        convergence_rate = 0.8 + data_factor * 0.1 - lr_penalty * 0.2
        convergence_rate = max(0.0, min(1.0, convergence_rate))
        
        # Create result
        transfer_id = f"transfer_{config.config_id}"
        
        result = TransferResult(
            transfer_id=transfer_id,
            config_id=config.config_id,
            model_id=config.model_id,
            target_task=config.target_task,
            performance=performance,
            accuracy=accuracy,
            loss=max(0.0, min(1.0, loss)),
            training_time=training_time,
            convergence_rate=convergence_rate,
            final_lr=config.learning_rate,
            metrics={
                "val_accuracy": accuracy * 0.98,
                "val_loss": loss * 1.05
            }
        )
        
        self.transfer_results[transfer_id] = result
        return result


# ==================== Main ====================

def main():
    """Simple demo of Transfer Learning Integration."""
    print("=" * 70)
    print("🔄 Transfer Learning Integration - Demo")
    print("=" * 70)
    print()
    
    # Create integrator
    integrator = TransferLearningIntegrator()
    
    # List available models
    print("📚 Available Pretrained Models")
    print("-" * 70)
    for model_id, model in integrator.models.items():
        print(f"  {model.name}:")
        print(f"    ID: {model.model_id}")
        print(f"    Task: {model.task_type}, Arch: {model.architecture}")
        print(f"    Accuracy: {model.accuracy:.2f}, Params: {model.num_parameters:,}")
        print(f"    Features: {model.features_dim}D")
        print()
    
    # Select model for classification
    print("🎯 Model Selection")
    print("-" * 70)
    selected = integrator.select_model(target_task="classification", preferred_architecture="cnn")
    if selected:
        print(f"  ✅ Selected: {selected.name}")
        print(f"     Accuracy: {selected.accuracy:.2f}")
    
    # Extract features
    print("\n🔍 Feature Extraction")
    print("-" * 70)
    extraction = integrator.extract_features(
        model_id=selected.model_id,
        input_id="sample_input_1",
        layer="last_hidden"
    )
    print(f"  ✅ Extracted {len(extraction.features)} features from {extraction.layer}")
    print(f"     Sample: {extraction.features[:5]}")
    
    # Create fine-tuning config
    print("\n⚙️  Fine-Tuning Configuration")
    print("-" * 70)
    ft_config = integrator.create_finetuning_config(
        model_id=selected.model_id,
        target_task="custom_classification",
        learning_rate=0.001,
        epochs=5,
        freeze_layers=["conv1", "conv2"]
    )
    print(f"  ✅ Config created: {ft_config.config_id}")
    print(f"     Target task: {ft_config.target_task}")
    print(f"     LR: {ft_config.learning_rate}, Epochs: {ft_config.epochs}")
    print(f"     Frozen layers: {ft_config.freeze_layers}")
    
    # Fine-tune
    print("\n🚀 Fine-Tuning")
    print("-" * 70)
    result = integrator.fine_tune_model(ft_config, target_data_size=2000)
    print(f"  ✅ Fine-tuning completed")
    print(f"     Performance: {result.performance:.3f}")
    print(f"     Accuracy: {result.accuracy:.3f}, Loss: {result.loss:.3f}")
    print(f"     Training time: {result.training_time:.2f}s")
    print(f"     Convergence: {result.convergence_rate:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Transfer Learning Integration demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
