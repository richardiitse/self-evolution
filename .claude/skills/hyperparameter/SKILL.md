# Hyperparameter Optimization Skill

自动超参数优化 - 使用多种优化算法自动调优超参数以获得最佳性能。

## 触发方式

```bash
# Claude Code
/hyperparameter --search-space=<json> [--algorithm=bayesian] [--max-iterations=50]

# OpenClaw (HTTPS Gateway)
POST /api/skills/hyperparameter
{
  "search_space": {
    "learning_rate": {"type": "float", "min": 1e-5, "max": 1e-1, "scale": "log"},
    "batch_size": {"type": "int", "min": 16, "max": 256, "step": 16}
  },
  "algorithm": "bayesian",
  "max_iterations": 50
}

# NanoClaw (MCP)
mcp__self_evolution_hyperparameter({
  "search_space": {...},
  "algorithm": "bayesian"
})
```

## 功能

- **多种优化算法**: 支持 Random、Grid、Bayesian 搜索
- **超参数重要性分析**: 自动分析超参数对性能的影响
- **跨任务迁移**: 将优化的超参数迁移到其他任务

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| search_space | object | 必需 | 超参数搜索空间定义 |
| algorithm | string | bayesian | 优化算法 (random/grid/bayesian) |
| max_iterations | int | 50 | 最大迭代次数 |

## 搜索空间定义

```json
{
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
  "optimizer": {
    "type": "categorical",
    "choices": ["adam", "sgd", "rmsprop"]
  }
}
```

## 输出

```markdown
## ⚙️ Hyperparameter Optimization Report

### 🔍 Search Configuration
- Algorithm: Bayesian Optimization
- Iterations: 50
- Search space: 6 parameters

### 📊 Best Configuration
- Performance: 0.923
- learning_rate: 0.000324
- batch_size: 64
- dropout_rate: 0.21

### 📈 Performance Progression
- Initial: 0.712
- Best: 0.923
- Improvement: +29.6%

### ⏱️ Timing
- Total time: 324.5s
- Average per iteration: 6.49s
```

## 算法对比

| 算法 | 适用场景 | 收敛速度 | 质量 |
|------|---------|---------|------|
| Random | 快速探索 | 慢 | 中等 |
| Grid | 细粒度搜索 | 中等 | 高 |
| Bayesian | 平衡效率与质量 | 快 | 高 |

## 系统兼容性

| 系统 | 支持状态 | 备注 |
|------|---------|------|
| Claude Code | ✅ | 原生支持 |
| OpenClaw | ✅ | HTTPS Gateway |
| NanoClaw | ✅ | MCP stdio |
