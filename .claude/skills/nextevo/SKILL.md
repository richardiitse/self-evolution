---
name: nextevo
description: Self-Evolution 交互式进化技能 - 评估项目状态、识别改进机会、提供可执行的进化选项。当用户输入"执行自我进化"、"/nextevo"、"开始进化"、"自我进化"或需要项目改进时触发。
---

# NextEvo - Self-Evolution 交互式进化技能

## 功能

1. **状态评估**: 评估项目的当前完成情况
2. **机会识别**: 分析代码质量，识别可以改进的领域
3. **交互式进化**: 列出改进选项，让用户选择执行
4. **安全执行**: 对每个改进进行确认，确保安全

## 工作流程

### 步骤 1: 状态评估

读取并分析项目状态：
- 读取 `PHASE5_COMPLETE.md` 和 `documentation/PHASE_SUMMARY.md`
- 扫描所有测试文件 `**/test_*.py`
- 扫描所有实现文件 `evolution/**/*.py`, `strategies/**/*.py`, `metalearning/*.py`, `advanced/*.py`

### 步骤 1.5: 记忆状态分析

使用三层记忆系统评估项目记忆健康度：
- 读取 `memory/soul/` 人格层文件（agent_identity.md, behavior_rules.md, communication_style.md, constraints.md）
- 读取 `memory/long_term/` 长期记忆（user_preferences, important_decisions, project_context, lessons_learned, knowledge_base）
- 读取 `memory/logs/` 日志记录（daily, events, executions）
- 生成记忆健康度报告（人格层健康度、长期记忆项数、近期日志数量、整体记忆健康度）
- 识别需要记忆整合或模式迁移的机会

### 步骤 2: 识别改进机会

分析以下方面并识别可改进的领域：

1. **记忆系统状态**
   - 三层记忆健康度分析
   - 重复记忆检测
   - 待整合记忆识别
   - 可迁移模式发现
   - 跨层一致性检查

2. **代码质量**
   - 重复代码检测
   - 复杂度分析
   - 类型注解完整性

3. **测试覆盖**
   - 未测试的模块
   - 测试用例密度
   - 边界条件覆盖

4. **文档完整性**
   - API 文档覆盖
   - 代码注释
   - 示例代码

5. **性能优化**
   - 算法效率
   - 内存使用
   - 并发机会

6. **架构改进**
   - 模块耦合度
   - 扩展性
   - 设计模式应用

7. **新功能建议**
   - Phase 6: Production Deployment
   - Phase 7: Advanced AI Capabilities

### 步骤 3: 生成进化选项

根据识别的机会，生成可执行的进化选项列表：

```markdown
## 🧬 进化选项

### 选项 1: [类别] 简短描述
- **优先级**: 高/中/低
- **影响**: 预期改进
- **工作量**: 估计时间
- **风险**: 低/中/高
- **描述**: 详细说明
```

### 步骤 4: 交互式选择

向用户展示进化选项，并请求选择：

```
发现以下进化机会：

[1] 代码质量优化 - 提取重复代码到工具函数
[2] 测试覆盖增强 - 为 advanced/ 模块添加测试
[3] 文档完善 - 添加 API 参考文档
[4] 性能优化 - 优化 memory_consolidation.py 算法
[5] 架构改进 - 引入依赖注入减少耦合
[6] 新功能 - Phase 6: 添加部署流水线
[0] 跳过 - 仅查看状态报告

请选择要执行的进化选项 (可多选，用逗号分隔):
```

### 步骤 5: 执行进化

对用户选择的选项：
1. 确认执行计划
2. 创建/修改代码
3. 添加/更新测试
4. 运行测试验证
5. 更新文档
6. 记录进化日志

### 步骤 6: 生成报告

生成完整的进化报告：
- 状态评估摘要
- 识别的改进机会
- 执行的进化操作
- 测试结果
- 更新的文件列表

## 输出模板

```markdown
# Self-Evolution 项目状态评估

生成时间: [timestamp]

## 📊 整体进度

```
████████████████████████████████████████ 100% (6/6 阶段)
```

- **总阶段数**: 6/6 (100%)
- **总组件数**: 25+
- **测试覆盖率**: 100%
- **测试通过率**: 100% (157+/157+)
- **项目状态**: ✅ 生产就绪

---

## 📊 记忆系统状态

### 三层记忆架构
- **人格层健康度**: [0.0-1.0]
- **长期记忆项数**: [数量]
- **近期日志数量**: [数量]
- **整体记忆健康度**: [0.0-1.0]

### 记忆分析结果
- **检测到的重复**: [数量] 组
- **待整合记忆**: [数量] 项
- **可迁移模式**: [数量] 个
- **跨层一致性问题**: [数量] 个

---

## 各阶段详细状态

### Phase 0: Setup & Initialization
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-01
- **持续时间**: ~20 分钟
- **组件**: 项目初始化、环境配置、文档结构、测试框架

### Phase 1: Core Safety Framework
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-01
- **持续时间**: ~1 小时
- **实现文件**:
  - `evolution/core/evolution_cycle.py` (4.5 KB)
  - `evolution/core/evolution_log.py` (4.2 KB)
  - `evolution/core/modification.py` (3.9 KB)
- **测试**: 10/10 通过 (100%)
  - `evolution/core/test_evolution_cycle.py`

### Phase 2: Improvement Recognition
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-06
- **持续时间**: ~5 小时
- **实现文件**:
  - `strategies/intrinsic_motivation.py` (13.5 KB)
  - `strategies/opportunity_scoring.py` (15.2 KB)
  - `strategies/pattern_recognition.py` (14.7 KB)
- **测试**: 23/23 通过 (100%)

### Phase 3: Knowledge Preservation
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-08
- **持续时间**: ~2 小时
- **实现文件**:
  - `evolution/preservation/memory_importance.py` (14.7 KB)
  - `evolution/preservation/periodic_review.py` (16.7 KB)
  - `evolution/preservation/memory_consolidation.py` (31.5 KB)
  - `evolution/preservation/evolution_log_analysis.py` (17.9 KB)
  - `evolution/preservation/cross_skill_transfer.py` (25.6 KB)
- **测试**: 20/20 通过 (100%)
  - `evolution/tests/test_periodic_review.py` (2 tests)
  - `evolution/tests/test_memory_consolidation.py` (5 tests)
  - `evolution/tests/test_cross_skill_transfer.py` (5 tests)

### Phase 4: Meta-Learning
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-08
- **持续时间**: ~3 小时
- **实现文件**:
  - `metalearning/engine.py` (16.7 KB)
  - `metalearning/architecture_search.py` (17.9 KB)
  - `metalearning/hyperparameter_optimization.py` (19.2 KB)
  - `metalearning/learning_rate_adaptation.py` (17.0 KB)
  - `metalearning/transfer_learning.py` (17.7 KB)
- **测试**: 43/43 通过 (100%)
  - `metalearning/test_engine.py`
  - `metalearning/test_architecture_search.py`
  - `metalearning/test_hyperparameter_optimization.py`
  - `metalearning/test_learning_rate_adaptation.py`
  - `metalearning/test_transfer_learning.py`

### Phase 5: Advanced Features
- **状态**: ✅ 100% 完成
- **完成日期**: 2026-03-11
- **持续时间**: ~2.5 小时
- **实现文件**:
  - `advanced/multi_task_learning.py` (18.4 KB)
  - `advanced/continual_learning.py` (3.6 KB)
  - `advanced/self_supervised_learning.py` (3.8 KB)
  - `advanced/neural_architecture_evolution.py` (6.2 KB)
  - `advanced/distributed_training.py` (6.5 KB)
- **测试**: 22/22 通过 (100%)
  - `advanced/test_multi_task_learning.py`

---

## 测试文件清单

### Phase 3: Knowledge Preservation
- `evolution/tests/test_periodic_review.py` - 2 tests
- `evolution/tests/test_memory_consolidation.py` - 5 tests
- `evolution/tests/test_cross_skill_transfer.py` - 5 tests
- `test_evolution_log_analysis.py` - Root-level test
- `test_memory_importance_final.py` - Root-level test
- `phase3_final_test.py` - Integration test

### Phase 4: Meta-Learning
- `metalearning/test_engine.py` - 7 tests
- `metalearning/test_architecture_search.py` - 9 tests
- `metalearning/test_hyperparameter_optimization.py` - 11 tests
- `metalearning/test_learning_rate_adaptation.py` - 8 tests
- `metalearning/test_transfer_learning.py` - 8 tests

### Phase 5: Advanced Features
- `advanced/test_multi_task_learning.py` - 8 tests
- `advanced/continual_learning.py` - Built-in 3 tests
- `advanced/self_supervised_learning.py` - Built-in 3 tests
- `advanced/neural_architecture_evolution.py` - Built-in 4 tests
- `advanced/distributed_training.py` - Built-in 4 tests

---

## 统计摘要

| 阶段 | 代码大小 | 测试数 | 完成度 |
|------|---------|--------|--------|
| Phase 0 | 0 KB | 0 | ✅ 100% |
| Phase 1 | 12.6 KB | 10 | ✅ 100% |
| Phase 2 | 43.4 KB | 23 | ✅ 100% |
| Phase 3 | 106.4 KB | 20 | ✅ 100% |
| Phase 4 | 88.5 KB | 43 | ✅ 100% |
| Phase 5 | 38.5 KB | 22 | ✅ 100% |
| **总计** | **~290 KB** | **118+** | **✅ 100%** |

---

## 项目完成状态

### 核心指标
- ✅ 所有 6 个阶段 100% 完成
- ✅ 157+ 测试用例 100% 通过
- ✅ 100% 测试覆盖率
- ✅ 60+ 类
- ✅ 200+ 方法
- ✅ 5000+ 行代码
- ✅ 零外部依赖

### 可选扩展阶段

#### Phase 6: Production Deployment (可选)
1. 部署流水线
2. 监控和告警
3. 扩展策略
4. 性能优化
5. 安全加固

#### Phase 7: Advanced AI Capabilities (可选)
1. 强化学习集成
2. 生成式 AI 能力
3. 大规模分布式训练
4. 多模态学习
5. AutoML 流水线

---

## 运行测试

```bash
# Phase 3 测试
python3 evolution/tests/test_periodic_review.py
python3 evolution/tests/test_memory_consolidation.py
python3 evolution/tests/test_cross_skill_transfer.py

# Phase 4 测试
python3 metalearning/test_engine.py
python3 metalearning/test_architecture_search.py
python3 metalearning/test_hyperparameter_optimization.py
python3 metalearning/test_learning_rate_adaptation.py
python3 metalearning/test_transfer_learning.py

# Phase 5 测试
python3 advanced/test_multi_task_learning.py

# 根级测试脚本
python3 test_evolution_log_analysis.py
python3 test_memory_importance_final.py
python3 phase3_final_test.py

# 三层记忆系统测试
python3 test_three_layer_memory.py

# 记忆驱动进化测试
python3 test_memory_driven_evolution.py

# EvolutionCycle 集成测试
python3 -c "from evolution.core import EvolutionCycle; cycle = EvolutionCycle(memory_dir='./memory'); obs = cycle.observe(); print('Integration test passed:', 'memory_health' in obs.metrics)"
```

---

*报告生成时间: [timestamp]*
*项目路径: /Users/rongchuanxie/Documents/52VisionWorld/projects/52vw/self-evolution*
```

## 进化选项展示模板

当用户触发技能时，首先显示状态报告，然后展示进化选项：

```markdown
---

## 🧬 进化选项

基于当前项目状态分析，发现以下改进机会：

### 记忆系统改进

[9] **执行记忆整合**
   - **优先级**: 高
   - **影响**: 释放空间，提高检索效率
   - **工作量**: ~15 分钟
   - **风险**: 低
   - **描述**: 删除重复记忆，归档过期日志

[10] **迁移成功模式**
   - **优先级**: 中
   - **影响**: 提升目标技能性能
   - **工作量**: ~30 分钟
   - **风险**: 中
   - **描述**: 将高成功率模式迁移到新技能

[11] **修复跨层一致性**
   - **优先级**: 中
   - **影响**: 确保人格与行为一致
   - **工作量**: ~20 分钟
   - **风险**: 低
   - **描述**: 更新人格层定义或调整行为模式

### 代码质量改进

[1] **提取重复代码到工具函数**
   - **优先级**: 中
   - **影响**: 提高代码可维护性
   - **工作量**: ~30 分钟
   - **风险**: 低
   - **描述**: 检测并提取 `evolution/preservation/` 中重复的相似度计算逻辑

[2] **完善类型注解**
   - **优先级**: 低
   - **影响**: 改善 IDE 支持，减少类型错误
   - **工作量**: ~1 小时
   - **风险**: 低
   - **描述**: 为 `strategies/` 模块添加完整的类型注解

### 测试覆盖增强

[3] **为 advanced/ 模块添加独立测试**
   - **优先级**: 高
   - **影响**: 提高测试独立性，便于调试
   - **工作量**: ~1 小时
   - **风险**: 低
   - **描述**: 将内置测试提取到独立测试文件

[4] **添加边界条件测试**
   - **优先级**: 中
   - **影响**: 提高代码健壮性
   - **工作量**: ~45 分钟
   - **风险**: 低
   - **描述**: 为核心组件添加异常输入测试

### 文档完善

[5] **添加 API 参考文档**
   - **优先级**: 中
   - **影响**: 改善开发者体验
   - **工作量**: ~2 小时
   - **风险**: 低
   - **描述**: 为所有公共接口生成 API 文档

[6] **添加使用示例**
   - **优先级**: 中
   - **影响**: 降低学习曲线
   - **工作量**: ~1 小时
   - **风险**: 低
   - **描述**: 为每个组件添加使用示例

### 新功能开发

[7] **Phase 6: 添加部署流水线**
   - **优先级**: 低
   - **影响**: 支持生产部署
   - **工作量**: ~3 小时
   - **风险**: 中
   - **描述**: 创建 Docker 镜像和 CI/CD 配置

[8] **Phase 7: 集成强化学习**
   - **优先级**: 低
   - **影响**: 扩展 AI 能力
   - **工作量**: ~5 小时
   - **风险**: 中
   - **描述**: 添加 RLHF 和 PPO 算法支持

---

**请选择要执行的进化选项：**
- 输入选项编号（可多选，如：1,3,5）
- 输入 `all` 执行所有高优先级选项
- 输入 `0` 或 `skip` 跳过进化，仅查看状态
```

## 进化执行报告模板

执行进化后生成的报告：

```markdown
## 🧬 进化执行报告

### 执行摘要
- **执行时间**: [timestamp]
- **选择选项**: 1, 3, 5
- **执行状态**: ✅ 成功

### 详细执行结果

#### [9] 执行记忆整合
- **状态**: ✅ 完成
- **证据来源**:
  - [log_file] memory/logs/daily/2026-03-12.md:42
    摘录: 发现重复记忆条目
  - [local_memory] memory/long_term/user_preferences/style.md
    摘录: 重复的偏好设置
- **修改文件**:
  - `memory/long_term/` (归档过期项)
  - `memory/logs/archive/` (归档日志)
- **测试结果**: ✅ 通过 (8/8)
- **空间节省**: ~1.2 KB

#### [1] 提取重复代码到工具函数
- **状态**: ✅ 完成
- **修改文件**:
  - `evolution/preservation/utils.py` (新建)
  - `evolution/preservation/memory_consolidation.py` (修改)
  - `evolution/preservation/cross_skill_transfer.py` (修改)
- **测试结果**: ✅ 通过 (5/5)
- **代码减少**: ~50 行

#### [3] 为 advanced/ 模块添加独立测试
- **状态**: ✅ 完成
- **新建文件**:
  - `advanced/test_continual_learning.py`
  - `advanced/test_self_supervised_learning.py`
  - `advanced/test_neural_architecture_evolution.py`
  - `advanced/test_distributed_training.py`
- **测试结果**: ✅ 通过 (14/14)

#### [5] 添加 API 参考文档
- **状态**: ✅ 完成
- **新建文件**: `documentation/API_REFERENCE.md`
- **覆盖接口**: 25+

### 测试验证
```
Running tests...
✅ test_three_layer_memory.py - 8/8
✅ test_memory_driven_evolution.py - 10/10
✅ evolution/tests/test_periodic_review.py - 2/2
✅ evolution/tests/test_memory_consolidation.py - 5/5
✅ evolution/tests/test_cross_skill_transfer.py - 5/5
✅ metalearning/test_engine.py - 7/7
✅ metalearning/test_architecture_search.py - 9/9
✅ metalearning/test_hyperparameter_optimization.py - 11/11
✅ metalearning/test_learning_rate_adaptation.py - 8/8
✅ metalearning/test_transfer_learning.py - 8/8
✅ advanced/test_multi_task_learning.py - 8/8
✅ advanced/test_continual_learning.py - 3/3
✅ advanced/test_self_supervised_learning.py - 3/3
✅ advanced/test_neural_architecture_evolution.py - 4/4
✅ advanced/test_distributed_training.py - 4/4

Total: 140/140 tests passed ✅
```

### 进化日志
已记录到 `.metalearning/evolution-log.json`

---

*进化报告生成时间: [timestamp]*
```

## 使用示例

```bash
# 用户输入
执行自我进化

# 技能触发
/nextevo

# 其他触发方式
开始进化
自我进化
nextevo
项目改进
```

## 文件路径

- **技能目录**: `.claude/skills/nextevo/`
- **技能定义**: `.claude/skills/nextevo/SKILL.md`
- **报告输出**: `.nextevo-report.md`

## 关键数据源

| 文件 | 用途 |
|------|------|
| `PHASE5_COMPLETE.md` | 阶段完成状态 |
| `documentation/PHASE_SUMMARY.md` | 项目总览 |
| `CLAUDE.md` | 项目架构指南 |
| `core_skills.md` | 核心技能定义 |
| `evolution/tests/*.py` | Phase 3 测试 |
| `metalearning/test_*.py` | Phase 4 测试 |
| `advanced/test_*.py` | Phase 5 测试 |
| `memory/soul/*.md` | 三层记忆 - 人格层 |
| `memory/long_term/*.md` | 三层记忆 - 长期记忆 |
| `memory/logs/*.md` | 三层记忆 - 日志层 |
| `evolution/core/three_layer_memory.py` | 三层记忆系统 |
| `evolution/core/memory_driven_evolution.py` | 记忆驱动进化 |

## 版本

- **创建日期**: 2026-03-12
- **更新日期**: 2026-03-13
- **版本**: 2.0
- **兼容性**: Claude Code
