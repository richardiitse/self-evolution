# Initialize Skill

技能初始化 - 检查和验证 self-evolution 项目的 memory 目录结构和人格设置（SOUL.md）。

## 触发方式

```bash
# Claude Code
/initialize [--memory-dir ./memory] [--fix]

# OpenClaw (HTTPS Gateway)
POST /api/skills/initialize
{
  "memory_dir": "./memory",
  "fix": false
}

# NanoClaw (MCP)
mcp__self_evolution_initialize({
  "memory_dir": "./memory",
  "fix": false
})
```

## 功能

- **检查目录结构**: 验证 memory/、memory/soul/、memory/long_term/、memory/logs/ 是否存在
- **验证人格文件**: 检查 SOUL.md 和人格子文件（agent_identity.md, behavior_rules.md, communication_style.md, constraints.md）
- **完整性评分**: 计算人格层完整性得分（0.0 - 1.0）
- **内容验证**: 验证人格文件大小是否符合规范（200-5000字符）
- **修复建议**: 提供清晰的修复命令和步骤

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------------|
| memory_dir | string | ./memory | Memory 目录路径 |
| fix | boolean | false | 自动修复缺失项 |

## 安全性

- **只读检查**: 默认只检查不修改
- **自动修复可选**: 使用 `--fix` 标志启用自动修复
- **备份机制**: 修复前自动备份现有文件

## 输出

### 健康状态输出

```markdown
## 🎭 Skill Initialization Report

**Generated:** 2026-03-13 10:45:00

### 📁 Directory Structure Check
- ✅ memory/ exists
- ✅ memory/soul/ exists
- ✅ memory/long_term/ exists
- ✅ memory/logs/ exists

### 📄 Soul Files Check
- ✅ SOUL.md found (2403 bytes)
- ✅ agent_identity.md found (1286 bytes)
- ✅ behavior_rules.md found (1464 bytes)
- ✅ communication_style.md found (1618 bytes)
- ✅ constraints.md found (1757 bytes)

### 🎯 Completeness Score: 1.00 (100%)
### ✨ Status: HEALTHY
```

### 缺失项输出

```markdown
## 🎭 Skill Initialization Report

### 🚨 Critical Issues Found

#### Issue 1: Missing memory/soul/SOUL.md
**Severity:** CRITICAL
**Fix:**
```bash
# Check if backup exists
ls memory/soul/*.md

# Or recreate from template
cp .claude/skills/initialize/templates/SOUL.template.md memory/soul/SOUL.md
```
```

## 系统兼容性

| 系统 | 支持状态 | 备注 |
|------|---------|------|
| Claude Code | ✅ | 原生支持 |
| OpenClaw | ✅ | HTTPS Gateway |
| NanoClaw | ✅ | MCP stdio |
