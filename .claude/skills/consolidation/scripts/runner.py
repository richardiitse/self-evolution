#!/usr/bin/env python3
"""
Consolidation Skill - Runner

执行记忆整合的核心脚本，集成现有的 run_consolidation.py 逻辑。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 scripts 目录到 Python 路径（用于绝对导入）
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from run_consolidation import MemoryConsolidator
from adapter import SystemAdapter


def run_consolidation(params: dict) -> dict:
    """
    执行记忆整合

    Args:
        params: 参数字典，包含 workspace, dry_run, confirm, archive_dir

    Returns:
        执行结果字典
    """
    workspace = params.get("workspace", Path.cwd())
    dry_run = params.get("dry_run", True)
    archive_dir = params.get("archive_dir", ".archives")

    # 创建整合器
    consolidator = MemoryConsolidator(
        workspace=Path(workspace),
        archive_dir=Path(archive_dir) if archive_dir else None
    )

    # 执行整合
    result = consolidator.perform_consolidation(dry_run=dry_run)

    # 转换为字典格式
    return {
        "items_processed": result.items_processed,
        "duplicate_groups": len(result.deleted_items) // 2 if result.deleted_items else 0,
        "archive_candidates": len(result.archived_items) if result.archived_items else 0,
        "deleted_items": result.deleted_items,
        "archived_items": result.archived_items,
        "merged_items": result.merged_items,
        "space_saved": result.space_saved,
        "time_taken": result.time_taken,
        "dry_run": dry_run
    }


def main():
    """主函数"""
    try:
        # 检测系统
        system = SystemAdapter.detect()

        # 解析参数
        params = SystemAdapter.parse_input(system)

        # 执行整合
        result = run_consolidation(params)

        # 格式化输出
        output = SystemAdapter.format_output(system, result)
        print(output)

        # 返回适当的退出码
        if result.get("items_processed", 0) == 0:
            sys.exit(1)  # 没有处理任何项目
        else:
            sys.exit(0)

    except Exception as e:
        # 格式化错误
        system = SystemAdapter.detect()
        error_output = SystemAdapter.format_error(system, e, error_code=-32001)
        print(error_output, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
