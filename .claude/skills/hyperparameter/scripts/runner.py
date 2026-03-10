#!/usr/bin/env python3
"""
Hyperparameter Optimization Skill - Runner

执行超参数优化的核心脚本，集成现有的 hyperparameter_optimization.py 逻辑。
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

from metalearning.hyperparameter_optimization import (
    HyperparameterOptimizer,
    HyperparameterSpace,
    HyperparameterConfig
)
from adapter import SystemAdapter


def run_hyperparameter_optimization(params: dict) -> dict:
    """
    执行超参数优化

    Args:
        params: 参数字典，包含 search_space, algorithm, max_iterations

    Returns:
        执行结果字典
    """
    import time

    search_space_def = params.get("search_space")
    algorithm = params.get("algorithm", "bayesian")
    max_iterations = params.get("max_iterations", 50)

    # 创建搜索空间
    if search_space_def:
        search_space = HyperparameterSpace(parameters=search_space_def)
    else:
        # 使用默认搜索空间
        search_space = None

    # 创建优化器
    optimizer = HyperparameterOptimizer(search_space=search_space)

    # 执行优化
    start_time = time.time()

    if algorithm == "random":
        results = optimizer.random_search(num_iterations=max_iterations)
    elif algorithm == "grid":
        results = optimizer.grid_search()
    else:  # bayesian (default)
        results = optimizer.bayesian_search(num_iterations=max_iterations)

    total_time = time.time() - start_time

    # 获取最佳配置
    best_configs = optimizer.get_best_configs(n=5)

    # 构建结果
    result = {
        "algorithm": algorithm,
        "iterations": len(results),
        "num_parameters": len(optimizer.search_space.parameters),
        "total_time": total_time,
        "avg_time_per_iter": total_time / len(results) if results else 0,
        "best_performance": optimizer.best_performance,
        "initial_performance": results[0].performance if results else 0,
    }

    # 添加最佳配置详情
    if best_configs:
        best_config, best_result = best_configs[0]
        result["best_config"] = best_config.to_dict()
        result["best_params"] = best_config.parameters

    # 添加前N配置
    result["top_configs"] = [
        {
            "performance": res.performance,
            "parameters": cfg.parameters
        }
        for cfg, res in best_configs
    ]

    return result


def main():
    """主函数"""
    try:
        # 检测系统
        system = SystemAdapter.detect()

        # 解析参数
        params = SystemAdapter.parse_input(system)

        # 验证必需参数
        if not params.get("search_space"):
            raise ValueError("search_space parameter is required")

        # 执行优化
        result = run_hyperparameter_optimization(params)

        # 格式化输出
        output = SystemAdapter.format_output(system, result)
        print(output)

        # 返回适当的退出码
        if result.get("best_performance", 0) > 0:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        # 格式化错误
        system = SystemAdapter.detect()
        error_output = SystemAdapter.format_error(system, e, error_code=-32002)
        print(error_output, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
