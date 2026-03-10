# Self-Evolution Usage Guide

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Usage](#advanced-usage)
4. [Examples](#examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Basic Evolution

```python
from evolution.core import EvolutionCycle

# Create evolution cycle
evolution = EvolutionCycle(
    workspace_path="/path/to/your/project",
    log_file="evolution.log"
)

# Run evolution
result = evolution.run_evolution(
    num_iterations=100,
    safety_checks=True
)

print(f"Evolution completed: {result['success']}")
print(f"Changes applied: {result['changes_applied']}")
```

### Meta-Learning

```python
from metalearning.engine import MetaLearningEngine

# Create meta-learning engine
engine = MetaLearningEngine()

# Create and complete task
task = engine.create_task(
    name="Hyperparameter Search",
    description="Search for optimal hyperparameters",
    phase="phase4",
    task_type="hyperopt"
)

result = engine.complete_task(
    task.task_id,
    success=True,
    performance=0.85,
    artifacts={"best_params": {...}},
    metrics={"accuracy": 0.85, "loss": 0.15},
    duration=120.5
)
```

## 📖 Basic Usage

### 1. Start Evolution

```python
from evolution.core import EvolutionCycle

# Initialize
evolution = EvolutionCycle()

# Run with default settings
result = evolution.run_evolution()
```

### 2. Configure Safety

```python
from evolution.core import EvolutionCycle

# Configure safety
evolution = EvolutionCycle(
    safety_level="strict",  # "strict", "moderate", "minimal"
    auto_rollback=True,  # Auto rollback on failure
    backup_before_change=True
)

# Run with safety
result = evolution.run_evolution(
    num_iterations=50,
    auto_confirm=False  # Require manual confirmation
)
```

### 3. Monitor Progress

```python
from evolution.core import EvolutionCycle

evolution = EvolutionCycle()

# Subscribe to events
def on_iteration_complete(event):
    print(f"Iteration {event.iteration} complete")
    print(f"  Performance: {event.performance}")

evolution.on("iteration_complete", on_iteration_complete)

# Run evolution
result = evolution.run_evolution(num_iterations=10)
```

## 🎯 Advanced Usage

### Multi-Task Learning

```python
from advanced.multi_task_learning import MultiTaskLearner

# Create learner
learner = MultiTaskLearner(shared_dim=128)

# Add tasks
task1 = learner.add_task(
    name="Image Classification",
    input_dim=784,
    output_dim=10,
    task_type="classification",
    loss_weight=1.0
)

task2 = learner.add_task(
    name="Sentiment Analysis",
    input_dim=300,
    output_dim=2,
    task_type="classification",
    loss_weight=0.8
)

# Prepare data
task_data = {
    task1.task_id: (inputs1, targets1),
    task2.task_id: (inputs2, targets2)
}

# Train all tasks
result = learner.train_tasks(
    task_data=task_data,
    num_epochs=100,
    learning_rate=0.01,
    balance_tasks=True
)
```

### Continual Learning

```python
from advanced.continual_learning import ContinualLearner

# Create continual learner
learner = ContinualLearner()

# Train tasks sequentially
for i in range(5):
    perf = learner.train_task(
        task_id=f"task_{i+1}",
        inputs=[...],
        targets=[...],
        epochs=50
    )
    print(f"Task {i+1} performance: {perf:.3f}")

# Get summary
summary = learner.get_summary()
print(f"Average performance: {summary.average_performance:.3f}")
print(f"Total forgetting: {summary.total_forgetting:.3f}")
```

### Neural Architecture Evolution

```python
from advanced.neural_architecture_evolution import NeuralArchitectureEvolver

# Create evolver
evolver = NeuralArchitectureEvolver()

# Evolve architectures
result = evolver.evolve(
    num_generations=10,
    population_size=20
)

print(f"Best architecture: {result.best_architecture}")
print(f"Best performance: {result.best_performance:.3f}")
```

## 📊 Examples

### Example 1: Complete Evolution Cycle

```python
from evolution.core import EvolutionCycle
from strategies.intrinsic_motivation import IntrinsicMotivation
from metalearning.engine import MetaLearningEngine

# Setup evolution
evolution = EvolutionCycle()

# Add motivation module
motivation = IntrinsicMotivation()
evolution.add_module("motivation", motivation)

# Add meta-learning
engine = MetaLearningEngine()
evolution.add_module("metalearning", engine)

# Run evolution
result = evolution.run_evolution(
    num_iterations=100,
    auto_confirm=True
)

# Print results
print(f"Evolution Result:")
print(f"  Success: {result['success']}")
print(f"  Iterations: {result['iterations']}")
print(f"  Changes Applied: {result['changes_applied']}")
print(f"  Performance Improvement: {result['performance_improvement']:.2f}")
```

### Example 2: Knowledge Preservation

```python
from evolution.preservation import MemoryConsolidator
from evolution.preservation import MemoryImportanceScorer

# Create preservation components
scorer = MemoryImportanceScorer()
consolidator = MemoryConsolidator()

# Scan memory
memory_items = scan_memory("/path/to/memory")

# Score importance
for item in memory_items:
    score = scorer.score_item(item)
    print(f"{item.name}: {score.score:.3f}")

# Consolidate memory
result = consolidator.perform_consolidation(
    memory_items=memory_items,
    dry_run=False
)

print(f"Consolidated: {len(result.deleted_items)} items deleted")
print(f"Archived: {len(result.archived_items)} items archived")
```

### Example 3: Transfer Learning

```python
from metalearning.transfer_learning import TransferLearningIntegrator

# Create integrator
integrator = TransferLearningIntegrator()

# Select pretrained model
model = integrator.select_model(
    target_task="classification",
    preferred_architecture="cnn"
)

# Extract features
extraction = integrator.extract_features(
    model_id=model.model_id,
    input_id="input_1",
    layer="last_hidden"
)

# Create fine-tuning config
ft_config = integrator.create_finetuning_config(
    model_id=model.model_id,
    target_task="new_task",
    learning_rate=0.001,
    epochs=10
)

# Fine-tune
result = integrator.fine_tune_model(
    config=ft_config,
    target_data_size=2000
)

print(f"Transfer Result:")
print(f"  Performance: {result.performance:.3f}")
print(f"  Accuracy: {result.accuracy:.3f}")
print(f"  Training Time: {result.training_time:.2f}s")
```

## 🔧 Best Practices

### 1. Safety First

Always run with safety checks:

```python
evolution = EvolutionCycle(
    safety_level="strict",
    auto_rollback=True,
    auto_confirm=False  # Don't auto-approve critical changes
)
```

### 2. Gradual Evolution

Start with conservative settings:

```python
# Conservative start
result = evolution.run_evolution(
    num_iterations=10,
    safety_checks=True,
    auto_confirm=False
)

# Then increase cautiously
result = evolution.run_evolution(
    num_iterations=50,
    safety_checks=True,
    auto_confirm=True
)
```

### 3. Monitor Closely

Use monitoring throughout:

```python
def monitor_progress(event):
    if event.type == "iteration_complete":
        print(f"Iteration {event.iteration}: {event.performance:.3f}")
    elif event.type == "change_applied":
        print(f"Change: {event.change_type}")
    elif event.type == "warning":
        print(f"WARNING: {event.message}")

evolution.on("*", monitor_progress)
```

### 4. Backup Before Major Changes

```python
# Enable automatic backup
evolution = EvolutionCycle(
    backup_before_change=True,
    backup_location="/path/to/backups"
)
```

### 5. Use Appropriate Safety Level

```python
# Development: moderate
evolution_dev = EvolutionCycle(safety_level="moderate")

# Testing: strict
evolution_test = EvolutionCycle(safety_level="strict")

# Production: strict
evolution_prod = EvolutionCycle(safety_level="strict", auto_confirm=False)
```

## 🐛 Troubleshooting

### Issue: Evolution Not Starting

**Symptom**: Nothing happens after `run_evolution()`

**Solution**:
```python
# Check workspace exists
evolution = EvolutionCycle(
    workspace_path="/valid/path/to/workspace"
)

# Check permissions
chmod +x /path/to/workspace

# Try with verbose mode
result = evolution.run_evolution(verbose=True)
```

### Issue: Changes Keep Being Rolled Back

**Symptom**: Changes always get rolled back

**Solution**:
```python
# Lower safety level temporarily
evolution = EvolutionCycle(
    safety_level="moderate"  # Start with moderate
)

# Review validation rules
result = evolution.get_validation_rules()
print(f"Rules: {result}")
```

### Issue: Memory Usage Too High

**Symptom**: System runs out of memory

**Solution**:
```python
# Limit resource usage
evolution = EvolutionCycle(
    max_memory="2GB",
    max_cpu=2,
    batch_size=16
)
```

### Issue: Evolution Too Slow

**Symptom**: Evolution takes too long

**Solution**:
```python
# Reduce iterations and increase batch size
result = evolution.run_evolution(
    num_iterations=50,  # Reduce
    batch_size=64,     # Increase
    parallel_workers=2  # Enable parallelism
)
```

## 📝 Logging and Debugging

### Enable Verbose Logging

```python
import logging

# Set log level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run with verbose
result = evolution.run_evolution(verbose=True)
```

### Save Evolution Logs

```python
# Logs are automatically saved
evolution = EvolutionCycle(
    log_file="evolution.log"
)

# Parse logs later
with open("evolution.log", "r") as f:
    for line in f:
        print(line)
```

## 🔒 Security Considerations

### Never Run Unsafe Evolution

```python
# Always use safety checks
result = evolution.run_evolution(
    safety_checks=True,
    auto_confirm=False
)
```

### Review Changes Before Applying

```python
# Get planned changes
changes = evolution.get_planned_changes()

# Review each change
for change in changes:
    print(f"Change: {change.type}")
    print(f"  File: {change.file}")
    print(f"  Diff: {change.diff}")
    
    # Approve manually
    response = input(f"Approve this change? (yes/no): ")
    if response.lower() != "yes":
        evolution.reject_change(change.id)
```

### Use Sandboxed Execution

```python
# Run in sandbox
evolution = EvolutionCycle(
    sandbox_enabled=True,
    sandbox_path="/path/to/sandbox"
)
```

## 🎓 Learning Resources

### Tutorials

1. [Basic Evolution Tutorial](tutorials/basic_evolution.md)
2. [Meta-Learning Guide](tutorials/meta_learning.md)
3. [Advanced Features Guide](tutorials/advanced_features.md)

### Examples

See `examples/` directory for:
- Basic evolution examples
- Multi-task learning examples
- Continual learning examples
- Transfer learning examples
- Neural architecture evolution examples

---

**Usage Guide Version**: 1.0.0  
**Last Updated**: 2026-03-08
