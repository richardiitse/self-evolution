#!/usr/bin/env python3
"""
Hyperparameter Optimization Skill - System Adapter

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
            "search_space": None,
            "algorithm": "bayesian",
            "max_iterations": 50
        }

        if system == "claude-code":
            # 优先从 stdin 读取 JSON 数据（用于测试）
            if not sys.stdin.isatty():
                try:
                    line = sys.stdin.readline()
                    if line:
                        data = json.loads(line)
                        params.update({
                            "search_space": data.get("search_space"),
                            "algorithm": data.get("algorithm", "bayesian"),
                            "max_iterations": data.get("max_iterations", 50)
                        })
                        return params
                except (json.JSONDecodeError, KeyError):
                    pass

            # 从命令行参数解析
            for i, arg in enumerate(sys.argv[1:], 1):
                if arg.startswith("--search-space="):
                    try:
                        params["search_space"] = json.loads(arg.split("=")[1])
                    except json.JSONDecodeError:
                        pass
                elif arg.startswith("--algorithm="):
                    params["algorithm"] = arg.split("=")[1]
                elif arg.startswith("--max-iterations="):
                    params["max_iterations"] = int(arg.split("=")[1])

        elif system == "openclaw":
            # 从 stdin JSON 读取
            try:
                data = json.load(sys.stdin)
                params.update({
                    "search_space": data.get("search_space"),
                    "algorithm": data.get("algorithm", "bayesian"),
                    "max_iterations": data.get("max_iterations", 50)
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
                        "search_space": params_data.get("search_space"),
                        "algorithm": params_data.get("algorithm", "bayesian"),
                        "max_iterations": params_data.get("max_iterations", 50)
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
            "## ⚙️ Hyperparameter Optimization Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # 搜索配置
        lines.extend([
            "### 🔍 Search Configuration",
            f"- Algorithm: {result.get('algorithm', 'unknown').title()}",
            f"- Iterations: {result.get('iterations', 0)}",
            f"- Search space: {result.get('num_parameters', 0)} parameters",
            ""
        ])

        # 最佳配置
        if result.get("best_config"):
            lines.extend([
                "### 📊 Best Configuration",
                f"- Performance: {result['best_config'].get('performance', 0):.3f}",
                ""
            ])
            for param, value in result.get("best_params", {}).items():
                if isinstance(value, float):
                    lines.append(f"- {param}: {value:.6f}")
                else:
                    lines.append(f"- {param}: {value}")
            lines.append("")

        # 性能进展
        if result.get("initial_performance") is not None:
            initial = result["initial_performance"]
            best = result.get("best_performance", 0)
            improvement = ((best - initial) / initial * 100) if initial > 0 else 0

            lines.extend([
                "### 📈 Performance Progression",
                f"- Initial: {initial:.3f}",
                f"- Best: {best:.3f}",
                f"- Improvement: {improvement:+.1f}%",
                ""
            ])

        # 时间统计
        lines.extend([
            "### ⏱️ Timing",
            f"- Total time: {result.get('total_time', 0):.1f}s",
            f"- Average per iteration: {result.get('avg_time_per_iter', 0):.2f}s",
            ""
        ])

        # 前N配置
        if result.get("top_configs"):
            lines.extend([
                "### 🏆 Top Configurations",
                ""
            ])
            for i, config in enumerate(result["top_configs"][:5], 1):
                lines.append(f"**{i}.** Performance: {config.get('performance', 0):.3f}")
                params_list = []
                for k, v in config.get("parameters", {}).items():
                    if isinstance(v, float):
                        params_list.append(f"{k}={v:.6f}")
                    else:
                        params_list.append(f"{k}={v}")
                params_str = ", ".join(params_list)
                lines.append(f"   {params_str}")
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
        "algorithm": "bayesian",
        "iterations": 50,
        "num_parameters": 6,
        "best_config": {"performance": 0.923},
        "best_params": {
            "learning_rate": 0.000324,
            "batch_size": 64,
            "dropout_rate": 0.21
        },
        "initial_performance": 0.712,
        "best_performance": 0.923,
        "total_time": 324.5,
        "avg_time_per_iter": 6.49,
        "top_configs": [
            {"performance": 0.923, "parameters": {"learning_rate": 0.000324}},
            {"performance": 0.915, "parameters": {"learning_rate": 0.000412}}
        ]
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
