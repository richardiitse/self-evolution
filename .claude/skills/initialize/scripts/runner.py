#!/usr/bin/env python3
"""
Initialize Skill - Runner

执行技能初始化检查的核心脚本，复用 three_layer_memory.py 中的组件。
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 scripts 目录到 Python 路径（用于绝对导入）
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from evolution.core.three_layer_memory import (
    ThreeLayerMemorySystem,
    SoulLayerReader,
    SoulLayerMemory,
    LongTermMemoryLayer,
    LogLayer
)
from adapter import SystemAdapter


class InitializationChecker:
    """初始化检查器 - 检查 memory 目录结构和人格文件"""

    # 预期的目录结构
    REQUIRED_DIRECTORIES = [
        "memory",
        "memory/soul",
        "memory/long_term",
        "memory/logs"
    ]

    # 预期的人格文件
    REQUIRED_SOUL_FILES = [
        "SOUL.md",
        "agent_identity.md",
        "behavior_rules.md",
        "communication_style.md",
        "constraints.md"
    ]

    # 预期的长期记忆子目录
    REQUIRED_LONG_TERM_SUBDIRS = [
        "user_preferences",
        "important_decisions",
        "project_context",
        "lessons_learned",
        "knowledge_base"
    ]

    def __init__(self, memory_dir: str = "./memory"):
        """
        初始化检查器

        Args:
            memory_dir: Memory 目录路径
        """
        self.memory_dir = Path(memory_dir)
        self.system = ThreeLayerMemorySystem(str(memory_dir))
        self.issues: List[Dict[str, Any]] = []

    def check_all(self) -> Dict[str, Any]:
        """
        执行所有检查，返回健康报告

        Returns:
            健康报告字典
        """
        result = {
            "directory_structure": self._check_directories(),
            "soul_files": self._check_soul_files(),
            "completeness_score": self._get_completeness_score(),
            "validation": self._validate_content(),
            "status": "UNKNOWN",
            "issues": []
        }

        # 收集所有问题
        self._collect_issues(result)

        # 确定总体状态
        result["status"] = self._determine_status(result)
        result["issues"] = self.issues

        return result

    def _check_directories(self) -> Dict[str, Dict[str, Any]]:
        """
        检查目录结构

        Returns:
            目录检查结果字典
        """
        result = {}

        for dir_path in self.REQUIRED_DIRECTORIES:
            full_path = self.memory_dir.parent / dir_path if not Path(dir_path).is_absolute() else Path(dir_path)
            exists = full_path.exists() and full_path.is_dir()

            result[dir_path] = {
                "exists": exists,
                "path": str(full_path),
                "message": "exists" if exists else "missing"
            }

        # 检查长期记忆子目录
        long_term_dir = self.memory_dir / "long_term"
        if long_term_dir.exists():
            for subdir in self.REQUIRED_LONG_TERM_SUBDIRS:
                full_path = long_term_dir / subdir
                exists = full_path.exists() and full_path.is_dir()

                result[f"memory/long_term/{subdir}"] = {
                    "exists": exists,
                    "path": str(full_path),
                    "message": "exists" if exists else "missing"
                }

        return result

    def _check_soul_files(self) -> Dict[str, Dict[str, Any]]:
        """
        检查人格文件

        Returns:
            人格文件检查结果字典
        """
        result = {}
        soul_dir = self.memory_dir / "soul"

        for filename in self.REQUIRED_SOUL_FILES:
            file_path = soul_dir / filename
            exists = file_path.exists() and file_path.is_file()
            size = file_path.stat().st_size if exists else 0

            result[filename] = {
                "exists": exists,
                "path": str(file_path),
                "size": size,
                "message": f"found ({size} bytes)" if exists else "missing"
            }

        return result

    def _get_completeness_score(self) -> float:
        """
        获取完整性得分

        Returns:
            完整性得分 (0.0 - 1.0)
        """
        try:
            soul = self.system.soul.load_identity()
            return soul.completeness_score
        except Exception:
            return 0.0

    def _validate_content(self) -> Dict[str, Any]:
        """
        验证内容有效性

        Returns:
            内容验证结果字典
        """
        try:
            soul = self.system.soul.load_identity()

            return {
                "is_valid": soul.is_valid,
                "total_size": soul.total_size,
                "size_valid": 200 <= soul.total_size <= 5000,
                "agent_identity_filled": bool(soul.agent_identity),
                "work_style_filled": bool(soul.work_style),
                "communication_style_filled": bool(soul.communication_style),
                "constraints_filled": bool(soul.constraints)
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }

    def _collect_issues(self, result: Dict[str, Any]) -> None:
        """收集所有问题"""
        # 检查缺失的目录
        for dir_name, status in result["directory_structure"].items():
            if not status.get("exists"):
                self.issues.append({
                    "type": "missing_directory",
                    "severity": "CRITICAL",
                    "title": f"Missing directory: {dir_name}",
                    "description": f"The required directory `{dir_name}` does not exist.",
                    "fix_commands": [
                        f"mkdir -p {status['path']}"
                    ]
                })

        # 检查缺失的人格文件
        for file_name, status in result["soul_files"].items():
            if not status.get("exists"):
                severity = "CRITICAL" if file_name == "SOUL.md" else "WARNING"
                self.issues.append({
                    "type": "missing_file",
                    "severity": severity,
                    "title": f"Missing file: {file_name}",
                    "description": f"The required file `{file_name}` does not exist in memory/soul/.",
                    "fix_commands": [
                        f"# Check if backup exists",
                        f"ls memory/soul/*.md",
                        "",
                        f"# Or recreate from template",
                        f"# touch memory/soul/{file_name}"
                    ]
                })

        # 检查内容验证问题
        validation = result.get("validation", {})
        if validation.get("size_valid") is False:
            self.issues.append({
                "type": "invalid_size",
                "severity": "WARNING",
                "title": "Soul layer size out of range",
                "description": f"Total size is {validation.get('total_size', 0)} characters. Expected range: 200-5000 characters.",
                "fix_commands": [
                    "# Edit the soul files to adjust content size",
                    "nano memory/soul/agent_identity.md",
                    "nano memory/soul/behavior_rules.md",
                    "nano memory/soul/communication_style.md"
                ]
            })

        # 检查完整性得分
        if result.get("completeness_score", 0) < 0.75:
            self.issues.append({
                "type": "low_completeness",
                "severity": "WARNING",
                "title": "Soul layer incomplete",
                "description": f"Completeness score is {result.get('completeness_score', 0):.2f}. Expected: 1.0.",
                "fix_commands": [
                    "# Fill in the missing soul files",
                    "nano memory/soul/agent_identity.md",
                    "nano memory/soul/behavior_rules.md",
                    "nano memory/soul/communication_style.md",
                    "nano memory/soul/constraints.md"
                ]
            })

    def _determine_status(self, result: Dict[str, Any]) -> str:
        """
        确定总体状态

        Returns:
            状态字符串 (HEALTHY/WARNING/CRITICAL)
        """
        # 检查是否有严重问题
        critical_issues = [i for i in self.issues if i.get("severity") == "CRITICAL"]
        if critical_issues:
            return "CRITICAL"

        # 检查是否有警告
        warning_issues = [i for i in self.issues if i.get("severity") == "WARNING"]
        if warning_issues:
            return "WARNING"

        # 检查完整性得分
        if result.get("completeness_score", 0) < 1.0:
            return "WARNING"

        return "HEALTHY"

    def fix_issues(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        修复发现的问题

        Args:
            dry_run: 如果为 True，只报告将要执行的操作

        Returns:
            修复结果字典
        """
        fix_results = {
            "directories_created": [],
            "files_created": [],
            "errors": []
        }

        for issue in self.issues:
            if issue["type"] == "missing_directory":
                dir_path = issue.get("title", "").split(": ")[1]
                full_path = self.memory_dir.parent / dir_path if not Path(dir_path).is_absolute() else Path(dir_path)

                if dry_run:
                    fix_results["directories_created"].append(str(full_path) + " (dry-run)")
                else:
                    try:
                        full_path.mkdir(parents=True, exist_ok=True)
                        fix_results["directories_created"].append(str(full_path))
                    except Exception as e:
                        fix_results["errors"].append(f"Failed to create {full_path}: {e}")

            elif issue["type"] == "missing_file":
                file_name = issue.get("title", "").split(": ")[1]
                file_path = self.memory_dir / "soul" / file_name

                if dry_run:
                    fix_results["files_created"].append(str(file_path) + " (dry-run)")
                else:
                    try:
                        # 确保父目录存在
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        # 创建空文件
                        file_path.touch()
                        fix_results["files_created"].append(str(file_path))
                    except Exception as e:
                        fix_results["errors"].append(f"Failed to create {file_path}: {e}")

        return fix_results


def run_initialize(params: dict) -> dict:
    """
    执行初始化检查

    Args:
        params: 参数字典，包含 memory_dir, fix

    Returns:
        执行结果字典
    """
    memory_dir = params.get("memory_dir", "./memory")
    fix = params.get("fix", False)

    # 创建检查器
    checker = InitializationChecker(memory_dir=str(memory_dir))

    # 执行检查
    result = checker.check_all()

    # 如果需要修复
    if fix:
        fix_results = checker.fix_issues(dry_run=False)
        result["fix_results"] = fix_results

    return result


def main():
    """主函数"""
    try:
        # 检测系统
        system = SystemAdapter.detect()

        # 解析参数
        params = SystemAdapter.parse_input(system)

        # 执行检查
        result = run_initialize(params)

        # 格式化输出
        output = SystemAdapter.format_output(system, result)
        print(output)

        # 返回适当的退出码
        if result.get("status") == "CRITICAL":
            sys.exit(1)
        elif result.get("status") == "WARNING":
            sys.exit(2)
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
