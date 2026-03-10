# Self-Evolution API Documentation

## 📚 API Overview

Self-Evolution provides a comprehensive API for autonomous self-improvement. The API is organized into modules corresponding to each phase of the system.

## 🚀 Quick Start

```python
from evolution.core import EvolutionCycle
from metalearning.engine import MetaLearningEngine
from advanced.multi_task_learning import MultiTaskLearner

# Create evolution cycle
evolution = EvolutionCycle()

# Run evolution
result = evolution.run_evolution(
    num_iterations=100,
    safety_checks=True
)
```

## 📋 Core API Modules

### Phase 0: Setup & Initialization

No specific API - initialization is automatic.

### Phase 1: Core Safety Framework

#### EvolutionCycle

Main orchestrator for the evolution cycle.

```python
from evolution.core.evolution_cycle import EvolutionCycle

evolution = EvolutionCycle(
    workspace_path="/path/to/workspace",
    log_file="evolution.log",
    max_iterations=1000,
    safety_level="strict"
)

# Run evolution
result = evolution.run_evolution(
    num_iterations=100,
    auto_confirm=False
)
```

**Methods:**
- `run_evolution(num_iterations, safety_checks=True)` - Run evolution cycle
- `get_status()` - Get current evolution status
- `pause_evolution()` - Pause evolution
- `resume_evolution()` - Resume evolution
- `stop_evolution()` - Stop evolution

#### SafetyValidator

Validates all changes before application.

```python
from evolution.core.evolution_cycle import SafetyValidator

validator = SafetyValidator(level="strict")

# Validate a change
result = validator.validate_change(
    change_type="code_modification",
    target="file.py",
    content="new_content"
)
```

**Methods:**
- `validate_change(change_type, target, content)` - Validate a change
- `validate_plan(plan)` - Validate an entire plan
- `get_validation_rules()` - Get current validation rules

### Phase 2: Improvement Recognition

#### IntrinsicMotivation

Calculates intrinsic motivation for exploration.

```python
from strategies.intrinsic_motivation import IntrinsicMotivation

motivation = IntrinsicMotivation()

# Calculate motivation
motivation_score = motivation.calculate_motivation(
    exploration_area="new_algorithms",
    performance_history=[...]
)
```

#### OpportunityScoring

Detects and scores improvement opportunities.

```python
from strategies.opportunity_scoring import OpportunityScoring

scorer = OpportunityScoring()

# Detect opportunities
opportunities = scorer.detect_opportunities(
    performance_metrics={...},
    codebase_analyzer={...}
)

# Score opportunities
scores = scorer.score_opportunities(opportunities)
```

### Phase 3: Knowledge Preservation

#### MemoryImportanceScorer

Scores memory items by importance.

```python
from evolution.preservation.memory_importance import MemoryImportanceScorer

scorer = MemoryImportanceScorer()

# Score a memory item
score = scorer.score_item(memory_item)
```

#### MemoryConsolidator

Consolidates memory by merging similar/duplicate items.

```python
from evolution.preservation.memory_consolidation import MemoryConsolidator

consolidator = MemoryConsolidator()

# Perform consolidation
result = consolidator.perform_consolidation(
    memory_items=[...],
    dry_run=False
)
```

### Phase 4: Meta-Learning

#### MetaLearningEngine

Orchestrates meta-learning across tasks.

```python
from metalearning.engine import MetaLearningEngine

engine = MetaLearningEngine()

# Create meta-learning task
task = engine.create_task(
    name="Hyperparameter Search",
    description="Search for optimal hyperparameters",
    phase="phase4",
    task_type="hyperopt"
)

# Run meta-learning
result = engine.complete_task(
    task.task_id,
    success=True,
    performance=0.85,
    artifacts={...},
    metrics={...},
    duration=120.5
)
```

#### ModelArchitectureSearch

Automatic neural architecture search.

```python
from metalearning.architecture_search import ModelArchitectureSearch

search = ModelArchitectureSearch()

# Perform architecture search
results = search.random_search(num_iterations=10)

# Get best architectures
best_archs = search.get_best_architectures(n=5)
```

#### HyperparameterOptimizer

Hyperparameter optimization engine.

```python
from metalearning.hyperparameter_optimization import HyperparameterOptimizer

optimizer = HyperparameterOptimizer()

# Perform random search
results = optimizer.random_search(num_iterations=10)

# Get best configurations
best_configs = optimizer.get_best_configs(n=5)
```

### Phase 5: Advanced Features

#### MultiTaskLearner

Multi-task learning engine.

```python
from advanced.multi_task_learning import MultiTaskLearner

learner = MultiTaskLearner(shared_dim=128)

# Add tasks
task1 = learner.add_task("Task1", input_dim=784, output_dim=10)
task2 = learner.add_task("Task2", input_dim=300, output_dim=2)

# Train tasks
result = learner.train_tasks(
    task_data={...},
    num_epochs=100
)
```

#### ContinualLearner

Continual learning engine.

```python
from advanced.continual_learning import ContinualLearner

learner = ContinualLearner()

# Train tasks sequentially
for i in range(5):
    perf = learner.train_task(
        task_id=f"task_{i+1}",
        inputs=[...],
        targets=[...],
        epochs=50
    )
    print(f"Task {i+1}: {perf:.3f}")

# Get summary
summary = learner.get_summary()
```

#### SelfSupervisedLearner

Self-supervised learning engine.

```python
from advanced.self_supervised_learning import SelfSupervisedLearner

learner = SelfSupervisedLearner()

# Pretrain with self-supervised learning
result = learner.pretrain(
    data=[...],
    method="contrastive",
    epochs=100
)
```

#### NeuralArchitectureEvolver

Neural architecture evolution engine.

```python
from advanced.neural_architecture_evolution import NeuralArchitectureEvolver

evolver = NeuralArchitectureEvolver()

# Evolve architectures
result = evolver.evolve(
    num_generations=10,
    population_size=20
)
```

#### DistributedTrainer

Distributed training engine.

```python
from advanced.distributed_training import DistributedTrainer

trainer = DistributedTrainer()

# Train in distributed manner
result = trainer.train_distributed(
    num_nodes=4,
    data_size_per_node=1000,
    batch_size=32,
    epochs=100
)
```

## 📊 Event System

Self-Evolution provides an event system for monitoring and reacting to evolution events.

### Event Types

```python
from evolution.core.evolution_cycle import EvolutionEvent

# Subscribe to events
def on_opportunity_detected(event):
    print(f"Opportunity detected: {event.data}")

def on_evolution_completed(event):
    print(f"Evolution completed: {event.result}")

# Event handlers
evolution.on("opportunity_detected", on_opportunity_detected)
evolution.on("evolution_completed", on_evolution_completed)
```

### Event Types

- `opportunity_detected` - New improvement opportunity detected
- `change_planned` - Change planned for execution
- `change_applied` - Change successfully applied
- `change_rolled_back` - Change rolled back
- `evolution_iteration_completed` - Iteration completed
- `evolution_completed` - Evolution cycle completed

## 🔒 Security & Safety

### Safety Checks

All API calls include safety checks:

```python
# Auto safety validation
result = evolution.run_evolution(
    num_iterations=10,
    safety_checks=True,  # Enable safety checks
    auto_confirm=False   # Require manual confirmation for dangerous operations
)
```

### Authorization

Critical operations require authorization:

```python
# Critical change requiring authorization
result = validator.validate_change(
    change_type="code_modification",
    target="critical_file.py",
    content="new_content",
    authorization_required=True
)
```

## 📈 Performance Monitoring

### Metrics Collection

```python
from evolution.core.evolution_cycle import PerformanceMonitor

monitor = PerformanceMonitor()

# Get performance metrics
metrics = monitor.get_performance_metrics(
    time_range="last_24h",
    granularity="hourly"
)
```

### Available Metrics

- `evolution_iterations` - Number of evolution iterations
- `changes_applied` - Number of changes applied
- `changes_rolled_back` - Number of changes rolled back
- `opportunities_found` - Number of opportunities found
- `performance_improvement` - Overall performance improvement
- `resource_usage` - CPU, memory, GPU usage
- `error_count` - Number of errors encountered

## 🧪 Testing API

### Test Helpers

```python
# Run all tests
python3 -m pytest evolution/tests/ -v
python3 -m pytest strategies/tests/ -v
python3 -m pytest metalearning/tests/ -v
python3 -m pytest advanced/tests/ -v

# Run specific test
python3 -m pytest evolution/tests/test_evolution_cycle.py::test_initialization -v
```

### Coverage

```bash
# Generate coverage report
python3 -m pytest --cov=evolution --cov=strategies --cov=metalearning --cov=advanced --cov-report=html

# View coverage
open htmlcov/index.html
```

## 📝 Examples

See [USAGE.md](USAGE.md) for detailed usage examples.

---

**API Version**: 1.0.0  
**Last Updated**: 2026-03-08  
**Status**: Stable
