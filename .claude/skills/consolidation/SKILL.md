# Consolidate Skill

工作区记忆整合 - 扫描重复文件、归档旧文件、生成整合报告。

## 触发方式

```bash
# Claude Code
/consolidate [--dry-run] [--confirm]

# OpenClaw (HTTPS Gateway)
POST /api/skills/consolidate
{
  "workspace": "/path/to/workspace",
  "dry_run": true,
  "archive_dir": ".archives"
}

# NanoClaw (MCP)
mcp__self_evolution_consolidate({
  "workspace": "/path/to/workspace",
  "dry_run": true
})
```

## 功能

- **扫描重复文件**: 基于文件名和内容查找重复文件
- **归档旧文件**: 将大文件或旧文件移动到归档目录
- **生成整合报告**: 输出详细的整合报告和建议

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| workspace | string | cwd | 工作区路径 |
| dry_run | boolean | true | 预览模式 |
| confirm | boolean | false | 执行整合 |
| archive_dir | string | .archives | 归档目录 |

## 安全性

- **dry-run 模式**: 默认启用，不会实际删除文件
- **确认机制**: 使用 `--confirm` 标志执行实际操作
- **排除模式**: 自动排除 `.git`、`__pycache__` 等目录

## 输出

```markdown
## 🧬 Memory Consolidation Report

### 📂 Scanned Items
- Total items: 150
- Duplicate groups: 5
- Archive candidates: 12

### 🗑️ Duplicates Found
- file1.py: 3 duplicates
- config.json: 2 duplicates

### 📦 Archive Candidates
- old_docs.md (15 days old, 120KB)
- temp_data.txt (500KB)

### ⚡ Summary
Would delete: 8 items
Would archive: 12 items
Space saved: 1.2MB
```

## 系统兼容性

| 系统 | 支持状态 | 备注 |
|------|---------|------|
| Claude Code | ✅ | 原生支持 |
| OpenClaw | ✅ | HTTPS Gateway |
| NanoClaw | ✅ | MCP stdio |
