# Self-Evolution Installation Guide

## 📦 System Requirements

### Minimum Requirements

- Python 3.8+
- 4GB RAM
- 10GB free disk space
- Linux/macOS/Windows

### Recommended Requirements

- Python 3.10+
- 8GB RAM
- 20GB free disk space
- Linux (Ubuntu 20.04+)
- SSD storage

### Optional Requirements

- CUDA-capable GPU (for deep learning components)
- Docker (for containerized deployment)
- Poetry or pip (for package management)

## 🚀 Installation Methods

### Method 1: Direct Installation

#### Step 1: Clone Repository

```bash
git clone https://github.com/openclaw/self-evolution.git
cd self-evolution
```

#### Step 2: Create Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n self-evolution python=3.10
conda activate self-evolution
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Run Tests

```bash
# Run all tests
python3 run_tests.py

# Run specific phase tests
python3 -m pytest evolution/tests/ -v
python3 -m pytest strategies/tests/ -v
python3 -m pytest metalearning/tests/ -v
python3 -m pytest advanced/tests/ -v
```

### Method 2: Pip Installation

```bash
# Install from PyPI (when available)
pip install openclaw-self-evolution
```

### Method 3: Docker Installation

#### Step 1: Build Docker Image

```bash
docker build -t self-evolution:latest .
```

#### Step 2: Run Container

```bash
docker run --rm -it self-evolution:latest bash
```

#### Step 3: Run Tests in Container

```bash
docker run --rm self-evolution:latest python3 run_tests.py
```

### Method 4: Development Installation

```bash
# Install in editable mode
cd self-evolution
pip install -e .
```

## 🔧 Configuration

### Environment Variables

```bash
# Workspace path
export SELF_EVOLUTION_WORKSPACE="/path/to/workspace"

# Log level
export SELF_EVOLUTION_LOG_LEVEL="INFO"

# Safety level
export SELF_EVOLUTION_SAFETY_LEVEL="strict"

# Resource limits
export SELF_EVOLUTION_MAX_MEMORY="4GB"
export SELF_EVOLUTION_MAX_CPU="4"
```

### Configuration Files

Create `config.yaml`:

```yaml
# Evolution Configuration
evolution:
  workspace_path: "/path/to/workspace"
  log_file: "evolution.log"
  max_iterations: 1000
  auto_confirm: false
  safety_checks: true

# Safety Configuration
safety:
  level: "strict"
  auto_rollback: true
  validation_rules:
    - "no_critical_changes_without_approval"
    - "no_deleting_source_code"
    - "no_modifying_safety_guards"

# Performance Configuration
performance:
  max_memory: "4GB"
  max_cpu: "4"
  monitoring_enabled: true
  metrics_interval: 60

# Logging Configuration
logging:
  level: "INFO"
  file: "self-evolution.log"
  console: true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## ✅ Verification

### Run Verification Script

```bash
python3 verify_installation.py
```

This will check:
- Python version compatibility
- All dependencies installed
- File permissions correct
- Tests can run successfully
- Configuration valid

### Expected Output

```
✅ Python version: 3.10.12
✅ All dependencies installed
✅ File permissions: OK
✅ Tests: PASSING (20/20)
✅ Configuration: VALID
```

## 🧪 Testing Installation

### Run Unit Tests

```bash
python3 -m pytest evolution/tests/ -v --tb=short
python3 -m pytest strategies/tests/ -v --tb=short
python3 -m pytest metalearning/tests/ -v --tb=short
python3 -m pytest advanced/tests/ -v --tb=short
```

### Run Integration Tests

```bash
python3 integration_test.py
```

### Run All Tests

```bash
python3 run_tests.py --verbose
```

## 🐛 Troubleshooting

### Issue: Import Error

**Symptom**: `ModuleNotFoundError: No module named 'evolution'`

**Solution**:
```bash
# Install in editable mode
pip install -e .
```

### Issue: Permission Denied

**Symptom**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Fix permissions
chmod +x run_tests.py
chmod -R +x evolution/
chmod -R +x strategies/
chmod -R +x metalearning/
chmod -R +x advanced/
```

### Issue: Tests Failing

**Symptom**: Tests failing with import errors

**Solution**:
```bash
# Ensure correct Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Issue: Out of Memory

**Symptom**: `MemoryError` during training

**Solution**:
```bash
# Reduce batch size
# Reduce number of layers
# Use gradient accumulation
# Enable memory optimization
```

## 🔒 Security Configuration

### Enable Safety Mode

```python
from evolution.core.evolution_cycle import EvolutionCycle

evolution = EvolutionCycle(safety_level="strict")
```

### Configure Rollback

```python
evolution = EvolutionCycle(
    safety_level="strict",
    auto_rollback=True,
    backup_before_change=True
)
```

### Set Resource Limits

```python
evolution = EvolutionCycle(
    max_memory="4GB",
    max_cpu=4,
    max_gpu_memory="8GB"
)
```

## 📦 Optional Dependencies

### For GPU Acceleration

```bash
pip install torch torchvision
pip install tensorflow-gpu
```

### For Advanced Logging

```bash
pip install loguru
pip install rich
```

### For Distributed Training

```bash
pip install horovod
pip install ray
```

### For Better Visualization

```bash
pip install tensorboard
pip install matplotlib
pip install seaborn
```

## 🚀 Quick Start

After installation, try this:

```python
from evolution.core import EvolutionCycle

# Create evolution cycle
evolution = EvolutionCycle()

# Run test evolution
result = evolution.run_evolution(
    num_iterations=10,
    safety_checks=True
)

print(f"Evolution status: {result['status']}")
```

## 📝 Next Steps

1. Read [USAGE.md](USAGE.md) for usage guide
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture
3. Check [API.md](API.md) for API documentation
4. See [PHASE_SUMMARY.md](PHASE_SUMMARY.md) for phase summaries

---

**Installation Version**: 1.0.0  
**Last Updated**: 2026-03-08
