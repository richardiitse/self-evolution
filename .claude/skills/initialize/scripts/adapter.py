#!/usr/bin/env python3
"""
Initialize Skill - System Adapter

统一适配器层，处理 Claude Code、OpenClaw、NanoClaw 三系统的差异。
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class SystemAdapter:
    """统一系统适配器基类"""

    SUPPORTED_SYSTEMS = ["claude-code", "openclaw", "nanoclaw"]

    @classmethod
    def detect(cls) -> str:
        """
        自动检测调用系统

        Returns:
            系统标识符 (claude-code/openclaw/nanoclaw)
        """
        # 检查环境变量
        if os.environ.get("CLAUDE_CODE"):
            return "claude-code"
        elif os.environ.get("OPENCLAW"):
            return "openclaw"
        elif os.environ.get("NANOCLAW") or os.environ.get("SKILL_TYPE") == "mcp":
            return "nanoclaw"

        # 检查命令行参数
        if len(sys.argv) > 1:
            if "--system=claude-code" in sys.argv:
                return "claude-code"
            elif "--system=openclaw" in sys.argv:
                return "openclaw"
            elif "--system=nanoclaw" in sys.argv:
                return "nanoclaw"

        # 默认为 claude-code
        return "claude-code"

    @classmethod
    def parse_input(cls, system: str) -> Dict[str, Any]:
        """
        解析系统特定参数

        Args:
            system: 系统标识符

        Returns:
            解析后的参数字典
        """
        params = {
            "memory_dir": "./memory",
            "fix": False
        }

        if system == "claude-code":
            # 从命令行参数解析
            for i, arg in enumerate(sys.argv[1:], 1):
                if arg == "--fix":
                    params["fix"] = True
                elif arg.startswith("--memory-dir="):
                    params["memory_dir"] = arg.split("=")[1]

        elif system == "openclaw":
            # 从 stdin JSON 读取
            try:
                data = json.load(sys.stdin)
                params.update({
                    "memory_dir": data.get("memory_dir", params["memory_dir"]),
                    "fix": data.get("fix", False)
                })
            except (json.JSONDecodeError, KeyError):
                pass

        elif system == "nanoclaw":
            # 从 MCP JSON-RPC 读取
            try:
                # MCP 通过 stdin 传递 JSON-RPC
                line = sys.stdin.readline()
                if line:
                    rpc = json.loads(line)
                    params_data = rpc.get("params", {})
                    params.update({
                        "memory_dir": params_data.get("memory_dir", params["memory_dir"]),
                        "fix": params_data.get("fix", False)
                    })
            except (json.JSONDecodeError, KeyError):
                pass

        return params

    @classmethod
    def format_output(cls, system: str, result: Dict[str, Any]) -> str:
        """
        格式化系统特定输出

        Args:
            system: 系统标识符
            result: 执行结果

        Returns:
            格式化后的输出字符串
        """
        if system == "claude-code":
            # Markdown 格式
            return cls._format_markdown(result)
        elif system == "openclaw":
            # JSON 格式
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif system == "nanoclaw":
            # MCP JSON-RPC 响应
            return json.dumps({
                "jsonrpc": "2.0",
                "id": result.get("id", 1),
                "result": result
            }, indent=2, ensure_ascii=False)

        return json.dumps(result, indent=2, ensure_ascii=False)

    @classmethod
    def format_error(cls, system: str, error: Exception, error_code: int = -32000) -> str:
        """
        格式化系统特定错误

        Args:
            system: 系统标识符
            error: 异常对象
            error_code: 错误代码

        Returns:
            格式化后的错误字符串
        """
        error_msg = str(error)

        if system == "claude-code":
            # Markdown 格式错误
            return f"## ❌ Error\n\n{error_msg}\n"
        elif system == "openclaw":
            # JSON 格式错误
            return json.dumps({
                "error": error_msg,
                "code": error_code
            }, indent=2, ensure_ascii=False)
        elif system == "nanoclaw":
            # MCP JSON-RPC 错误响应
            return json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": error_code,
                    "message": error_msg
                }
            }, indent=2, ensure_ascii=False)

        return error_msg

    @classmethod
    def _format_markdown(cls, result: Dict[str, Any]) -> str:
        """格式化为 Markdown 输出"""
        lines = [
            "## 🎭 Skill Initialization Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # 目录结构检查
        if "directory_structure" in result:
            lines.extend([
                "### 📁 Directory Structure Check",
                ""
            ])
            for dir_name, status in result["directory_structure"].items():
                icon = "✅" if status.get("exists") else "❌"
                lines.append(f"- {icon} {dir_name} {status.get('message', '')}")
            lines.append("")

        # 人格文件检查
        if "soul_files" in result:
            lines.extend([
                "### 📄 Soul Files Check",
                ""
            ])
            for file_name, status in result["soul_files"].items():
                icon = "✅" if status.get("exists") else "❌"
                size_info = f" ({status.get('size', 0)} bytes)" if status.get("size") else ""
                lines.append(f"- {icon} {file_name}{size_info}")
            lines.append("")

        # 完整性评分
        if "completeness_score" in result:
            score = result["completeness_score"]
            percentage = score * 100
            lines.extend([
                f"### 🎯 Completeness Score: {score:.2f} ({percentage:.0f}%)",
                ""
            ])

        # 总体状态
        if "status" in result:
            status = result["status"]
            icon = "✨" if status == "HEALTHY" else "⚠️"
            lines.extend([
                f"### {icon} Status: {status}",
                ""
            ])

        # 问题和建议
        if result.get("issues"):
            lines.extend([
                "### 🚨 Issues Found",
                ""
            ])
            for i, issue in enumerate(result["issues"], 1):
                severity = issue.get("severity", "INFO")
                lines.extend([
                    f"#### Issue {i}: {issue.get('title', 'Unknown')}",
                    f"**Severity:** {severity}",
                    ""
                ])
                if issue.get("description"):
                    lines.append(f"{issue['description']}")
                    lines.append("")
                if issue.get("fix_commands"):
                    lines.append("**Fix:**")
                    lines.append("```bash")
                    for cmd in issue["fix_commands"]:
                        lines.append(cmd)
                    lines.append("```")
                    lines.append("")

        return "\n".join(lines)


def main():
    """适配器主函数 - 用于测试"""
    system = SystemAdapter.detect()
    print(f"Detected system: {system}")

    # 测试参数解析
    params = SystemAdapter.parse_input(system)
    print(f"Parsed params: {params}")

    # 测试输出格式化
    result = {
        "directory_structure": {
            "memory/": {"exists": True},
            "memory/soul/": {"exists": True},
            "memory/long_term/": {"exists": True},
            "memory/logs/": {"exists": True}
        },
        "soul_files": {
            "SOUL.md": {"exists": True, "size": 2403},
            "agent_identity.md": {"exists": True, "size": 1286},
            "behavior_rules.md": {"exists": True, "size": 1464},
            "communication_style.md": {"exists": True, "size": 1618},
            "constraints.md": {"exists": True, "size": 1757}
        },
        "completeness_score": 1.0,
        "status": "HEALTHY",
        "issues": []
    }

    output = SystemAdapter.format_output(system, result)
    print("\nFormatted output:")
    print(output)

    # 测试错误格式化
    error = SystemAdapter.format_error(system, Exception("Test error"))
    print("\nFormatted error:")
    print(error)


if __name__ == "__main__":
    main()
