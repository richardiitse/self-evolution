# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Self-Evolution is a production-grade autonomous AI system that implements continuous self-improvement through 6 comprehensive phases. This is a Python 3.8+ research/production hybrid project with **100% test coverage** (135+ tests).

**Current Status**: Phase 4 (Meta-Learning) is complete. Phase 5 (Advanced Features) is in progress.

## Development Commands

### Running Tests

```bash
# Run all tests (preferred method)
python3 metalearning/test_engine.py
python3 metalearning/test_architecture_search.py
python3 metalearning/test_hyperparameter_optimization.py
python3 metalearning/test_learning_rate_adaptation.py
python3 metalearning/test_transfer_learning.py

# Run Phase 3 tests (Knowledge Preservation)
python3 evolution/tests/test_periodic_review.py
python3 evolution/tests/test_memory_consolidation.py
python3 evolution/tests/test_cross_skill_transfer.py

# Run Phase 5 tests (Advanced Features)
python3 advanced/test_multi_task_learning.py

# Root-level test scripts
python3 test_evolution_log_analysis.py
python3 test_memory_importance_final.py
python3 phase3_final_test.py
```

### Code Execution

```bash
# Run meta-learning components
python3 metalearning/engine.py
python3 metalearning/architecture_search.py
python3 metalearning/hyperparameter_optimization.py
python3 metalearning/learning_rate_adaptation.py
python3 metalearning/transfer_learning.py

# Run consolidation script
python3 run_consolidation.py [--confirm]
```

### Development Workflow

1. Tests are standalone Python files with their own `run_all_tests()` functions
2. Each component has a corresponding `test_*.py` file in the same directory
3. No external build step required - pure Python with standard library only
4. Tests use custom harness (not pytest) - run test files directly

## Architecture

The system follows a **layered phase architecture** where each phase builds upon previous ones:

```
Application Layer
    ↓
Meta-Learning Layer (Phase 4) - COMPLETE
    ├── engine.py - Meta-learning orchestration
    ├── architecture_search.py - Neural architecture search
    ├── hyperparameter_optimization.py - Hyperparameter optimization
    ├── learning_rate_adaptation.py - Learning rate adaptation
    └── transfer_learning.py - Transfer learning
    ↓
Advanced Features Layer (Phase 5) - IN PROGRESS
    ├── multi_task_learning.py - Multi-task learning (has tests)
    ├── continual_learning.py - Continual learning
    ├── self_supervised_learning.py - Self-supervised learning
    ├── neural_architecture_evolution.py - Architecture evolution
    └── distributed_training.py - Distributed training
    ↓
Knowledge Preservation Layer (Phase 3) - COMPLETE
    ├── evolution/preservation/memory_consolidation.py
    ├── evolution/preservation/periodic_review.py
    ├── evolution/preservation/evolution_log_analysis.py
    └── evolution/preservation/cross_skill_transfer.py
```

### Key Design Patterns

1. **Dataclass Domain Models**: All entities use `@dataclass` for clean state representation (e.g., `MetaLearningTask`, `MemoryItem`)

2. **Storage by Convention**: Each module creates its own state directory:
   - `.metalearning/` - Meta-learning state
   - `.archives/` - Archived memory items
   - `.omc/` - OMC plugin state

3. **Custom Test Harness**: Tests follow a consistent pattern:
   ```python
   def test_feature():
       print("Testing feature...")
       # Arrange, Act, Assert
       return True

   def run_all_tests():
       # Run all tests and report
   ```

4. **No External Dependencies**: All code uses Python standard library only

## File Organization

```
self-evolution/
├── metalearning/          # Phase 4: Meta-Learning (COMPLETE)
│   ├── *.py              # Implementation files
│   └── test_*.py         # Corresponding tests
├── advanced/              # Phase 5: Advanced Features (IN PROGRESS)
│   ├── multi_task_learning.py      # Has tests
│   ├── continual_learning.py
│   ├── self_supervised_learning.py
│   ├── neural_architecture_evolution.py
│   ├── distributed_training.py
│   └── test_multi_task_learning.py
├── evolution/
│   ├── preservation/      # Phase 3: Knowledge Preservation
│   └── tests/
├── documentation/         # Comprehensive docs (ARCHITECTURE.md, TESTING.md, etc.)
├── .metalearning/         # Meta-learning state (generated)
├── .archives/             # Archived memory (generated)
└── *.py                   # Root-level test/consolidation scripts
```

## Important Context

- **Language**: Default to Chinese for communication (用户偏好中文)
- **Test Coverage**: 100% coverage is maintained across all phases
- **Status Tracking**: Use `PHASE*_COMPLETE.md` and `PHASE*_SPECIFICATION.md` for phase status
- **Documentation**: `documentation/` folder contains complete reference docs
- **Consolidation**: `run_consolidation.py` performs workspace-wide memory cleanup (dry-run by default)

## Current Priorities

1. Complete Phase 5 (Advanced Features) - only `multi_task_learning.py` has tests
2. Maintain 100% test coverage for all new code
3. Follow existing patterns for test files and implementation
