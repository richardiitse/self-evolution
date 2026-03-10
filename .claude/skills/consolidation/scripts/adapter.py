#!/usr/bin/env python3
"""
Consolidation Skill - System Adapter

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
            "workspace": Path.cwd(),
            "dry_run": True,
            "confirm": False,
            "archive_dir": ".archives"
        }

        if system == "claude-code":
            # 从命令行参数解析
            for i, arg in enumerate(sys.argv[1:], 1):
                if arg == "--dry-run":
                    params["dry_run"] = True
                elif arg == "--confirm":
                    params["confirm"] = True
                    params["dry_run"] = False
                elif arg.startswith("--workspace="):
                    params["workspace"] = Path(arg.split("=")[1])
                elif arg.startswith("--archive-dir="):
                    params["archive_dir"] = arg.split("=")[1]

        elif system == "openclaw":
            # 从 stdin JSON 读取
            try:
                data = json.load(sys.stdin)
                params.update({
                    "workspace": Path(data.get("workspace", str(params["workspace"]))),
                    "dry_run": data.get("dry_run", True),
                    "confirm": data.get("confirm", False),
                    "archive_dir": data.get("archive_dir", ".archives")
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
                        "workspace": Path(params_data.get("workspace", str(params["workspace"]))),
                        "dry_run": params_data.get("dry_run", True),
                        "confirm": params_data.get("confirm", False),
                        "archive_dir": params_data.get("archive_dir", ".archives")
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
            "## 🧬 Memory Consolidation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # 扫描结果
        if "items_processed" in result:
            lines.extend([
                "### 📂 Scanned Items",
                f"- Total items: {result['items_processed']}",
                f"- Duplicate groups: {result.get('duplicate_groups', 0)}",
                f"- Archive candidates: {result.get('archive_candidates', 0)}",
                ""
            ])

        # 删除的文件
        if result.get("deleted_items"):
            lines.extend([
                "### 🗑️ Deleted Items",
                ""
            ])
            for item in result["deleted_items"][:10]:
                lines.append(f"- `{Path(item).name}`")
            if len(result["deleted_items"]) > 10:
                lines.append(f"- ... and {len(result['deleted_items']) - 10} more")
            lines.append("")

        # 归档的文件
        if result.get("archived_items"):
            lines.extend([
                "### 📦 Archived Items",
                ""
            ])
            for item in result["archived_items"][:10]:
                lines.append(f"- `{Path(item).name}`")
            if len(result["archived_items"]) > 10:
                lines.append(f"- ... and {len(result['archived_items']) - 10} more")
            lines.append("")

        # 总结
        lines.extend([
            "### ⚡ Summary",
            f"- Deleted: {len(result.get('deleted_items', []))} items",
            f"- Archived: {len(result.get('archived_items', []))} items",
            f"- Space saved: {result.get('space_saved', 0) / 1024:.1f} KB",
            f"- Time taken: {result.get('time_taken', 0):.2f}s",
            ""
        ])

        if result.get("dry_run"):
            lines.extend([
                "ℹ️ **Dry Run Mode** - No files were actually modified.",
                "Use `--confirm` to execute the consolidation."
            ])

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
        "items_processed": 100,
        "duplicate_groups": 5,
        "archive_candidates": 10,
        "deleted_items": ["file1.py", "file2.py"],
        "archived_items": ["old_doc.md"],
        "space_saved": 1024000,
        "time_taken": 2.5,
        "dry_run": True
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
