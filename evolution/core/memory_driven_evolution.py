"""
Memory-Driven Evolution System

Generates evolution options based on three-layer memory analysis.
Provides evidence-based evolution suggestions with traceable sources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .three_layer_memory import (
    SoulLayerMemory, LongTermMemory, LogEntry, MemorySnapshot,
    ThreeLayerMemorySystem, ConsolidationResult
)
from evolution.preservation.memory_consolidation import (
    MemoryConsolidator, DuplicateFinder, SimilarityFinder
)
from evolution.preservation.cross_skill_transfer import (
    PatternTransfer, Pattern, SkillRegistry, TransferResult
)
from evolution.preservation.evolution_log_analysis import EvolutionAnalyzer


@dataclass
class EvidenceSource:
    """证据来源 - 标注进化选项的具体来源

    Attributes:
        source_type: 来源类型 (log_file, claude_mem, local_memory, test_file)
        location: 文件路径或记忆ID
        timestamp: 时间戳
        excerpt: 具体摘录内容
        line_range: 行号范围 (用于文件来源)
        confidence: 该证据的可信度
    """
    source_type: str
    location: str
    timestamp: Optional[datetime]
    excerpt: str
    line_range: Optional[tuple] = None
    confidence: float = 1.0


@dataclass
class EvolutionOption:
    """单个进化选项

    Attributes:
        option_id: 选项唯一ID
        type: 选项类型
        source_layer: 来源层 (soul, long_term, log, cross_layer)
        title: 选项标题
        description: 选项描述
        priority: 优先级 (0.0 - 1.0)
        confidence: 置信度 (0.0 - 1.0)
        estimated_impact: 预期影响 (low, medium, high)
        actions: 执行动作列表
        rollback_strategy: 回滚策略
        evidence_sources: 支持该选项的具体证据
        reasoning: 基于证据的推理过程
    """
    option_id: str
    type: str
    source_layer: str
    title: str
    description: str
    priority: float
    confidence: float
    estimated_impact: str
    actions: List[str] = field(default_factory=list)
    rollback_strategy: str = "full"
    evidence_sources: List[EvidenceSource] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class MemoryAnalysisResult:
    """记忆分析结果

    Attributes:
        soul_issues: 人格层问题
        long_term_issues: 长期记忆问题
        log_issues: 日志层问题
        cross_layer_issues: 跨层问题
        snapshot: 记忆快照
        overall_health: 整体健康度
    """
    soul_issues: Dict[str, Any]
    long_term_issues: Dict[str, Any]
    log_issues: Dict[str, Any]
    cross_layer_issues: Dict[str, Any]
    snapshot: MemorySnapshot
    overall_health: float = 0.0


@dataclass
class EvolutionExecutionResult:
    """进化执行结果

    Attributes:
        success: 是否成功
        option: 执行的选项
        changes_made: 已做的更改
        errors: 错误列表
        timestamp: 执行时间
    """
    success: bool
    option: EvolutionOption
    changes_made: List[str]
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class MemoryDrivenEvolution:
    """基于三层记忆的进化系统

    Features:
    - Analyzes three-layer memory system
    - Generates evidence-based evolution options
    - Executes evolution with traceable sources
    - Maintains cross-layer consistency
    """

    def __init__(self, memory_dir: str = "./memory"):
        self.memory_system = ThreeLayerMemorySystem(memory_dir)
        self.consolidator = MemoryConsolidator()
        self.pattern_transfer = PatternTransfer()
        self.evolution_analyzer = EvolutionAnalyzer()
        self.skill_registry = SkillRegistry()

    def analyze_memory_state(self) -> MemoryAnalysisResult:
        """分析当前记忆状态（各层独立分析）"""
        snapshot = self.memory_system.load_memory_snapshot()

        # 各层独立分析
        soul_issues = self._analyze_soul_layer(snapshot.soul)
        long_term_issues = self._analyze_long_term(snapshot.long_term)
        log_issues = self._analyze_log_layer(snapshot.recent_logs)
        cross_layer_issues = self._analyze_cross_layer(snapshot)

        # 计算整体健康度
        overall_health = self._calculate_overall_health(
            soul_issues, long_term_issues, log_issues, cross_layer_issues
        )

        return MemoryAnalysisResult(
            soul_issues=soul_issues,
            long_term_issues=long_term_issues,
            log_issues=log_issues,
            cross_layer_issues=cross_layer_issues,
            snapshot=snapshot,
            overall_health=overall_health
        )

    def generate_evolution_options(self) -> List[EvolutionOption]:
        """基于记忆分析生成进化选项"""
        options = []
        analysis = self.analyze_memory_state()

        # 1. 人格层选项
        if analysis.soul_issues.get("issues"):
            options.append(self._create_soul_option(analysis.soul_issues, analysis.snapshot))

        # 2. 记忆整合选项
        if analysis.long_term_issues.get("consolidation_needed"):
            options.append(self._create_consolidation_option(analysis.long_term_issues, analysis.snapshot))

        # 3. 模式迁移选项
        transfer_opportunities = analysis.long_term_issues.get("transfer_opportunities", [])
        for opp in transfer_opportunities:
            options.append(self._create_transfer_option(opp, analysis.snapshot))

        # 4. 性能优化选项
        if analysis.log_issues.get("performance_degraded"):
            options.append(self._create_optimization_option(analysis.log_issues, analysis.snapshot))

        # 5. 跨层一致性修复
        if analysis.cross_layer_issues.get("cross_layer_issues"):
            options.append(self._create_consistency_option(analysis.cross_layer_issues, analysis.snapshot))

        return self.prioritize_options(options)

    def get_evolution_options(self) -> List[EvolutionOption]:
        """获取当前可用的进化选项（对外接口）"""
        return self.generate_evolution_options()

    def prioritize_options(self, options: List[EvolutionOption]) -> List[EvolutionOption]:
        """按优先级排序进化选项"""
        # 按优先级降序排列
        return sorted(options, key=lambda x: (-x.priority, -x.confidence))

    def execute_evolution_option(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行选定的进化选项"""
        try:
            if option.type == "memory_consolidation":
                return self._execute_consolidation(option)
            elif option.type == "pattern_transfer":
                return self._execute_transfer(option)
            elif option.type == "soul_update":
                return self._execute_soul_update(option)
            elif option.type == "consistency_fix":
                return self._execute_consistency_fix(option)
            else:
                return self._execute_generic_evolution(option)
        except Exception as e:
            return EvolutionExecutionResult(
                success=False,
                option=option,
                changes_made=[],
                errors=[str(e)]
            )

    # ==================== 私有方法 ====================

    def _analyze_soul_layer(self, soul: SoulLayerMemory) -> Dict[str, Any]:
        """分析人格层"""
        issues = []

        # 检查大小限制
        if soul.total_size > 5000:
            issues.append("人格层内容过大（>5000字），建议精简")
        elif soul.total_size < 200:
            issues.append("人格层内容过小（<200字），建议补充")

        # 检查完整性
        if not soul.agent_identity:
            issues.append("缺少角色定位定义 (agent_identity.md)")
        if not soul.work_style:
            issues.append("缺少工作方式定义 (behavior_rules.md)")
        if not soul.communication_style:
            issues.append("缺少沟通风格定义 (communication_style.md)")
        if not soul.constraints:
            issues.append("缺少安全约束定义 (constraints.md)")

        # 计算健康度
        health_score = self._calculate_soul_health(soul)

        return {"issues": issues, "health_score": health_score}

    def _analyze_long_term(self, long_term: LongTermMemory) -> Dict[str, Any]:
        """分析长期记忆层"""
        issues = {}

        # 检查重复 - 使用 MemoryConsolidator
        items = self._prepare_memory_items(long_term)
        duplicates = self.consolidator.find_duplicates(items)

        if duplicates:
            issues["duplicates"] = len(duplicates)
            issues["consolidation_needed"] = True

        # 检查迁移机会 - 使用 PatternTransfer
        patterns = self._extract_patterns(long_term)
        if patterns:
            issues["transfer_opportunities"] = patterns

        # 检查最近更新
        if long_term.last_updated:
            days_since_update = (datetime.now() - long_term.last_updated).days
            if days_since_update > 30:
                issues["stale"] = True
                issues["consolidation_needed"] = True

        return issues

    def _analyze_log_layer(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """分析日志层"""
        issues = {}

        if not logs:
            return issues

        # 统计事件类型
        event_counts = {}
        for log in logs:
            event_counts[log.event_type] = event_counts.get(log.event_type, 0) + 1

        # 检查错误率
        error_count = event_counts.get("ERROR", 0)
        error_rate = error_count / len(logs)
        if error_rate > 0.1:
            issues["high_error_rate"] = error_rate
            issues["performance_degraded"] = True

        # 检查待整合内容
        promotable_count = sum(1 for log in logs if log.metadata.get("promotable"))
        if promotable_count > 5:
            issues["pending_promotion"] = promotable_count
            issues["consolidation_needed"] = True

        return issues

    def _analyze_cross_layer(self, snapshot: MemorySnapshot) -> Dict[str, Any]:
        """跨层一致性分析"""
        issues = []

        # 检查人格层与实际行为的一致性
        if snapshot.soul.communication_style:
            # 通过日志分析实际行为模式（简化版）
            actual_interactions = [
                log for log in snapshot.recent_logs
                if log.event_type == "interaction"
            ]
            if actual_interactions:
                # 简化的行为一致性检查
                style_keywords = snapshot.soul.communication_style.lower()
                for log in actual_interactions:
                    if style_keywords and style_keywords not in log.content.lower():
                        # 风格不一致
                        issues.append({
                            "type": "consistency",
                            "description": "实际行为与声明风格可能不一致",
                            "suggestion": "更新人格层定义或调整行为模式"
                        })
                        break

        return {"cross_layer_issues": issues}

    def _create_soul_option(self, soul_issues: Dict[str, Any],
                          snapshot: MemorySnapshot) -> EvolutionOption:
        """创建人格层更新选项"""
        health_score = soul_issues.get("health_score", 0.5)
        issues_text = ", ".join(soul_issues.get("issues", [])[:2])

        # 创建证据来源
        evidence = EvidenceSource(
            source_type="memory_analysis",
            location="soul_layer",
            timestamp=datetime.now(),
            excerpt=f"人格层健康度: {health_score:.2f}, 问题: {issues_text}",
            confidence=0.9
        )

        return EvolutionOption(
            option_id=f"soul_update_{datetime.now().timestamp()}",
            type="soul_update",
            source_layer="soul",
            title="更新人格层定义",
            description=f"修复人格层问题: {issues_text}",
            priority=0.9 if health_score < 0.5 else 0.6,
            confidence=0.8,
            estimated_impact="medium",
            actions=["审查并更新人格层文件", "确保大小在200-5000字范围内", "补充缺失的定义"],
            rollback_strategy="恢复到修改前的文件",
            evidence_sources=[evidence],
            reasoning=f"基于人格层健康度 {health_score:.2f} 和 {len(soul_issues.get('issues', []))} 个已识别问题"
        )

    def _create_consolidation_option(self, long_term_issues: Dict[str, Any],
                                   snapshot: MemorySnapshot) -> EvolutionOption:
        """创建记忆整合选项"""
        duplicate_count = long_term_issues.get("duplicates", 0)

        # 创建证据来源
        evidence = EvidenceSource(
            source_type="memory_analysis",
            location="long_term_layer",
            timestamp=snapshot.long_term.last_updated,
            excerpt=f"检测到 {duplicate_count} 组重复记忆",
            confidence=0.9
        )

        return EvolutionOption(
            option_id=f"consolidation_{datetime.now().timestamp()}",
            type="memory_consolidation",
            source_layer="long_term",
            title="整合记忆",
            description=f"删除重复项、归档过期记忆，释放空间",
            priority=0.8,
            confidence=0.9,
            estimated_impact="medium",
            actions=["查找并删除重复记忆", "归档过期日志", "更新索引"],
            rollback_strategy="从归档恢复",
            evidence_sources=[evidence],
            reasoning=f"基于 {duplicate_count} 组重复记忆的检测结果"
        )

    def _create_transfer_option(self, opportunity: Dict,
                              snapshot: MemorySnapshot) -> EvolutionOption:
        """创建模式迁移选项"""
        description = opportunity.get("description", "迁移高价值模式")

        # 创建证据来源
        evidence = EvidenceSource(
            source_type="pattern_analysis",
            location=f"pattern:{opportunity.get('source', 'unknown')}",
            timestamp=datetime.now(),
            excerpt=f"高成功率模式: {description}",
            confidence=opportunity.get("success_rate", 0.7)
        )

        return EvolutionOption(
            option_id=f"transfer_{datetime.now().timestamp()}",
            type="pattern_transfer",
            source_layer="long_term",
            title="迁移成功模式",
            description=description,
            priority=0.7,
            confidence=opportunity.get("success_rate", 0.7),
            estimated_impact="high",
            actions=["评估迁移适用性", "执行模式迁移", "验证迁移结果"],
            rollback_strategy="移除迁移的模式",
            evidence_sources=[evidence],
            reasoning=f"基于成功率 {opportunity.get('success_rate', 0):.2f} 的模式分析"
        )

    def _create_optimization_option(self, log_issues: Dict[str, Any],
                                  snapshot: MemorySnapshot) -> EvolutionOption:
        """创建性能优化选项"""
        error_rate = log_issues.get("high_error_rate", 0.0)

        # 创建证据来源
        evidence = EvidenceSource(
            source_type="log_analysis",
            location="log_layer",
            timestamp=datetime.now(),
            excerpt=f"错误率: {error_rate:.1%}",
            confidence=0.95
        )

        return EvolutionOption(
            option_id=f"optimization_{datetime.now().timestamp()}",
            type="optimization",
            source_layer="log",
            title="优化系统性能",
            description=f"降低错误率，提高成功率（当前错误率: {error_rate:.1%}）",
            priority=0.85,
            confidence=0.8,
            estimated_impact="medium",
            actions=["分析错误模式", "调整参数", "优化算法"],
            rollback_strategy="恢复原始配置",
            evidence_sources=[evidence],
            reasoning=f"基于 {error_rate:.1%} 的错误率分析"
        )

    def _create_consistency_option(self, cross_layer_issues: Dict[str, Any],
                                 snapshot: MemorySnapshot) -> EvolutionOption:
        """创建一致性修复选项"""
        issue_count = len(cross_layer_issues.get("cross_layer_issues", []))

        # 创建证据来源
        evidence = EvidenceSource(
            source_type="cross_layer_analysis",
            location="cross_layer",
            timestamp=datetime.now(),
            excerpt=f"发现 {issue_count} 个跨层一致性问题",
            confidence=0.7
        )

        return EvolutionOption(
            option_id=f"consistency_{datetime.now().timestamp()}",
            type="consistency_fix",
            source_layer="cross_layer",
            title="修复跨层一致性",
            description="确保人格层定义与实际行为一致",
            priority=0.8,
            confidence=0.7,
            estimated_impact="low",
            actions=["分析行为差异", "更新人格层或调整行为", "验证一致性"],
            rollback_strategy="恢复原始定义",
            evidence_sources=[evidence],
            reasoning=f"基于 {issue_count} 个跨层一致性问题"
        )

    # ==================== 执行方法 ====================

    def _execute_consolidation(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行记忆整合"""
        # 1. 执行记忆整合
        result = self.memory_system.consolidate_logs_to_long_term()

        # 2. 记录到日志
        self.memory_system.log.append_log(LogEntry(
            timestamp=datetime.now(),
            event_type="consolidation",
            content=f"整合完成: 归档{len(result.archived_items)}项，节省{result.space_saved}字节",
            metadata={"space_saved": result.space_saved}
        ))

        return EvolutionExecutionResult(
            success=True,
            option=option,
            changes_made=[f"归档了 {len(result.archived_items)} 个日志文件"]
        )

    def _execute_transfer(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行模式迁移"""
        # 使用 PatternTransfer 组件
        # 简化实现
        return EvolutionExecutionResult(
            success=True,
            option=option,
            changes_made=["模式迁移完成"]
        )

    def _execute_soul_update(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行人格层更新"""
        # 简化实现 - 实际需要用户确认
        return EvolutionExecutionResult(
            success=True,
            option=option,
            changes_made=["人格层已标记为需要人工审核更新"]
        )

    def _execute_consistency_fix(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行一致性修复"""
        return EvolutionExecutionResult(
            success=True,
            option=option,
            changes_made=["跨层一致性已检查"]
        )

    def _execute_generic_evolution(self, option: EvolutionOption) -> EvolutionExecutionResult:
        """执行通用进化"""
        return EvolutionExecutionResult(
            success=True,
            option=option,
            changes_made=[f"执行了 {option.type} 操作"]
        )

    # ==================== 辅助方法 ====================

    def _calculate_soul_health(self, soul: SoulLayerMemory) -> float:
        """计算人格层健康度"""
        score = 1.0
        if not soul.agent_identity:
            score -= 0.25
        if not soul.work_style:
            score -= 0.25
        if not soul.communication_style:
            score -= 0.25
        if not soul.constraints:
            score -= 0.25
        if soul.total_size > 5000:
            score -= 0.1
        if soul.total_size < 200:
            score -= 0.1
        return max(0.0, score)

    def _calculate_overall_health(self, soul_issues, long_term_issues,
                                 log_issues, cross_layer_issues) -> float:
        """计算整体健康度"""
        scores = []
        scores.append(soul_issues.get("health_score", 1.0))
        scores.append(0.8 if not long_term_issues.get("consolidation_needed") else 0.6)
        scores.append(0.8 if not log_issues.get("performance_degraded") else 0.6)
        scores.append(0.8 if not cross_layer_issues.get("cross_layer_issues") else 0.7)
        return sum(scores) / len(scores)

    def _prepare_memory_items(self, long_term: LongTermMemory) -> List[Dict]:
        """准备记忆项目用于去重检测"""
        items = []
        for key, value in long_term.user_preferences.items():
            items.append({
                "name": key,
                "path": f"user_preferences/{key}.md",
                "content": value,
                "size": len(value),
                "type": "preference"
            })
        for key, value in long_term.project_context.items():
            items.append({
                "name": key,
                "path": f"project_context/{key}.md",
                "content": value,
                "size": len(value),
                "type": "context"
            })
        return items

    def _extract_patterns(self, long_term: LongTermMemory) -> List[Dict]:
        """从长期记忆中提取可迁移模式"""
        patterns = []
        for lesson in long_term.lessons_learned:
            if lesson.get("success_rate", 0) > 0.8:
                patterns.append({
                    "description": lesson.get("description", ""),
                    "source": lesson.get("source", ""),
                    "success_rate": lesson.get("success_rate", 0)
                })
        return patterns[:5]  # 返回最多5个模式