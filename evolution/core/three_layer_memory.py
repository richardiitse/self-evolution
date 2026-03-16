"""
Three-Layer Memory System for Autonomous Evolution

Architecture:
- Soul Layer: Agent identity and behavioral rules (200-5000 characters)
- Long-Term Memory: Stable information (preferences, decisions, lessons)
- Log Layer: Daily interaction records (append-only)

This system provides a structured approach to memory management, allowing
the autonomous system to organize, access, and evolve based on its past
experiences and learned patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil


@dataclass
class SoulLayerMemory:
    """人格层记忆 - AI Agent 的身份和行为准则

    Attributes:
        agent_identity: "我是谁" - 角色定位
        work_style: "我如何工作" - 工作方式
        communication_style: "我如何说话" - 沟通风格
        constraints: "我不能做什么" - 安全约束列表
    """
    agent_identity: str = ""
    work_style: str = ""
    communication_style: str = ""
    constraints: List[str] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        """返回总字符数"""
        return len(self.agent_identity) + len(self.work_style) + len(self.communication_style)

    @property
    def is_valid(self) -> bool:
        """检查人格层是否有效（200-5000字范围）"""
        return 200 <= self.total_size <= 5000

    @property
    def completeness_score(self) -> float:
        """计算完整性得分 (0.0 - 1.0)"""
        score = 0.0
        if self.agent_identity:
            score += 0.25
        if self.work_style:
            score += 0.25
        if self.communication_style:
            score += 0.25
        if self.constraints:
            score += 0.25
        return score


@dataclass
class LongTermMemory:
    """长期记忆 - 稳定的筛选信息

    Attributes:
        user_preferences: 用户偏好
        important_decisions: 重要决策记录
        project_context: 项目上下文
        lessons_learned: 经验教训
        knowledge_base: 知识库
        last_updated: 最后更新时间
    """
    user_preferences: Dict[str, str] = field(default_factory=dict)
    important_decisions: List[Dict] = field(default_factory=list)
    project_context: Dict[str, str] = field(default_factory=dict)
    lessons_learned: List[Dict] = field(default_factory=list)
    knowledge_base: Dict[str, str] = field(default_factory=dict)
    last_updated: Optional[datetime] = None

    @property
    def total_items(self) -> int:
        """返回记忆项总数"""
        return (
            len(self.user_preferences) +
            len(self.important_decisions) +
            len(self.project_context) +
            len(self.lessons_learned) +
            len(self.knowledge_base)
        )


@dataclass
class LogEntry:
    """日志条目

    Attributes:
        timestamp: 时间戳
        event_type: 事件类型 (interaction, execution, event, consolidation)
        content: 日志内容
        metadata: 附加元数据
    """
    timestamp: datetime
    event_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """完整记忆快照

    Attributes:
        soul: 人格层记忆
        long_term: 长期记忆
        recent_logs: 最近日志
        snapshot_time: 快照时间
    """
    soul: SoulLayerMemory
    long_term: LongTermMemory
    recent_logs: List[LogEntry]
    snapshot_time: datetime

    @property
    def health_score(self) -> float:
        """计算整体健康度 (0.0 - 1.0)"""
        soul_score = self.soul.completeness_score
        size_score = 1.0 if self.soul.is_valid else 0.5
        memory_score = min(self.long_term.total_items / 50.0, 1.0)
        return (soul_score + size_score + memory_score) / 3.0


@dataclass
class ConsolidationResult:
    """记忆整合结果

    Attributes:
        deleted_items: 删除的项目列表
        archived_items: 归档的项目列表
        merged_items: 合并的项目列表
        space_saved: 节省的空间（字节）
        time_taken: 执行时间（秒）
    """
    deleted_items: List[str]
    archived_items: List[str]
    merged_items: List[str]
    space_saved: int
    time_taken: float


class SoulLayerReader:
    """人格层读取器 - 加载 Agent 身份和行为准则"""

    def __init__(self, memory_dir: str):
        self.memory_dir = Path(memory_dir) / "soul"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def load_identity(self) -> SoulLayerMemory:
        """加载人格层记忆"""
        files_map = {
            "agent_identity.md": "agent_identity",
            "behavior_rules.md": "work_style",
            "communication_style.md": "communication_style",
        }

        identity_data = {}
        for file, key in files_map.items():
            path = self.memory_dir / file
            if path.exists():
                try:
                    identity_data[key] = path.read_text(encoding='utf-8').strip()
                except Exception:
                    identity_data[key] = ""

        # Parse constraints from file
        constraints = []
        constraints_file = self.memory_dir / "constraints.md"
        if constraints_file.exists():
            content = constraints_file.read_text(encoding='utf-8')
            constraints = [
                line.strip("- ").strip()
                for line in content.split('\n')
                if line.strip().startswith('-')
            ]

        return SoulLayerMemory(
            agent_identity=identity_data.get("agent_identity", ""),
            work_style=identity_data.get("work_style", ""),
            communication_style=identity_data.get("communication_style", ""),
            constraints=constraints
        )

    def save_identity(self, soul: SoulLayerMemory) -> None:
        """保存人格层记忆"""
        # Write identity files
        (self.memory_dir / "agent_identity.md").write_text(
            soul.agent_identity, encoding='utf-8'
        )
        (self.memory_dir / "behavior_rules.md").write_text(
            soul.work_style, encoding='utf-8'
        )
        (self.memory_dir / "communication_style.md").write_text(
            soul.communication_style, encoding='utf-8'
        )

        # Write constraints
        constraints_content = "\n".join(f"- {c}" for c in soul.constraints)
        (self.memory_dir / "constraints.md").write_text(
            constraints_content, encoding='utf-8'
        )


class LongTermMemoryLayer:
    """长期记忆层 - 存储稳定信息"""

    def __init__(self, memory_dir: str):
        self.memory_dir = Path(memory_dir) / "long_term"
        self.subdirs = {
            "user_preferences": self.memory_dir / "user_preferences",
            "important_decisions": self.memory_dir / "important_decisions",
            "project_context": self.memory_dir / "project_context",
            "lessons_learned": self.memory_dir / "lessons_learned",
            "knowledge_base": self.memory_dir / "knowledge_base"
        }
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> LongTermMemory:
        """加载长期记忆"""
        # Load user preferences
        user_preferences = self._load_markdown_files(
            self.subdirs["user_preferences"]
        )

        # Load important decisions
        important_decisions = self._load_json_file(
            self.subdirs["important_decisions"] / "decisions.json", []
        )

        # Load project context
        project_context = self._load_markdown_files(
            self.subdirs["project_context"]
        )

        # Load lessons learned
        lessons_learned = self._load_json_file(
            self.subdirs["lessons_learned"] / "lessons.json", []
        )

        # Load knowledge base
        knowledge_base = self._load_markdown_files(
            self.subdirs["knowledge_base"]
        )

        # Find last updated timestamp
        last_updated = self._find_last_updated()

        return LongTermMemory(
            user_preferences=user_preferences,
            important_decisions=important_decisions,
            project_context=project_context,
            lessons_learned=lessons_learned,
            knowledge_base=knowledge_base,
            last_updated=last_updated
        )

    def _load_markdown_files(self, directory: Path) -> Dict[str, str]:
        """加载目录下所有 .md 文件"""
        result = {}
        for file in directory.glob("*.md"):
            try:
                result[file.stem] = file.read_text(encoding='utf-8')
            except Exception:
                pass
        return result

    def _load_json_file(self, path: Path, default):
        """加载 JSON 文件"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def _find_last_updated(self) -> Optional[datetime]:
        """查找最后更新时间"""
        all_files = []
        for subdir in self.subdirs.values():
            all_files.extend(subdir.rglob("*"))

        timestamps = [f.stat().st_mtime for f in all_files if f.is_file()]
        if timestamps:
            return datetime.fromtimestamp(max(timestamps))
        return None

    def add_preference(self, key: str, value: str) -> None:
        """添加用户偏好"""
        path = self.subdirs["user_preferences"] / f"{key}.md"
        path.write_text(value, encoding='utf-8')

    def add_lesson(self, lesson: Dict[str, Any]) -> None:
        """添加经验教训"""
        lessons_file = self.subdirs["lessons_learned"] / "lessons.json"
        lessons = self._load_json_file(lessons_file, [])
        lesson['timestamp'] = datetime.now().isoformat()
        lessons.append(lesson)
        with open(lessons_file, 'w', encoding='utf-8') as f:
            json.dump(lessons, f, indent=2, ensure_ascii=False)


class LogLayer:
    """日志层 - 记录每日原始交互"""

    def __init__(self, memory_dir: str):
        self.log_dir = Path(memory_dir) / "logs"
        self.daily_dir = self.log_dir / "daily"
        self.events_dir = self.log_dir / "events"
        self.executions_dir = self.log_dir / "executions"

        for subdir in [self.log_dir, self.daily_dir, self.events_dir, self.executions_dir]:
            subdir.mkdir(parents=True, exist_ok=True)

    def load_recent_logs(self, days: int = 7) -> List[LogEntry]:
        """加载最近N天的日志"""
        logs = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            log_file = self.daily_dir / f"{date}.md"
            if log_file.exists():
                logs.extend(self._parse_log_file(log_file))
        return logs

    def append_log(self, entry: LogEntry):
        """追加日志（只追加不覆写）"""
        date = entry.timestamp.strftime("%Y-%m-%d")
        log_file = self.daily_dir / f"{date}.md"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{entry.timestamp.strftime('%H:%M:%S')}] {entry.event_type}: {entry.content}\n")

    def _parse_log_file(self, path: Path) -> List[LogEntry]:
        """解析日志文件"""
        logs = []
        try:
            content = path.read_text(encoding='utf-8')
            lines = content.split('\n')

            for line in lines:
                line = line.strip()
                if not line or not line.startswith('['):
                    continue

                # Parse format: [HH:MM:SS] EVENT_TYPE: content
                try:
                    # Extract timestamp
                    end_bracket = line.find(']')
                    time_str = line[1:end_bracket]
                    hour, minute, second = map(int, time_str.split(':'))

                    # Extract event type
                    rest = line[end_bracket + 1:].strip()
                    if ':' in rest:
                        event_type, content = rest.split(':', 1)
                        event_type = event_type.strip()
                        content = content.strip()

                        logs.append(LogEntry(
                            timestamp=datetime.now().replace(
                                hour=hour, minute=minute, second=second,
                                microsecond=0
                            ),
                            event_type=event_type,
                            content=content,
                            metadata={}
                        ))
                except Exception:
                    continue
        except Exception:
            pass

        return logs


class ThreeLayerMemorySystem:
    """三层记忆系统 - 统一管理三层记忆

    Architecture:
    - Soul Layer: 200-5000字符，定义身份和行为
    - Long-Term Memory: 稳定信息，可检索和更新
    - Log Layer: 每日记录，只追加不覆写
    """

    def __init__(self, memory_dir: str = "./memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.soul = SoulLayerReader(str(memory_dir))
        self.long_term = LongTermMemoryLayer(str(memory_dir))
        self.log = LogLayer(str(memory_dir))

    def load_memory_snapshot(self) -> MemorySnapshot:
        """加载完整记忆快照"""
        return MemorySnapshot(
            soul=self.soul.load_identity(),
            long_term=self.long_term.load_all(),
            recent_logs=self.log.load_recent_logs(),
            snapshot_time=datetime.now()
        )

    def consolidate_logs_to_long_term(self, days_threshold: int = 30) -> ConsolidationResult:
        """将过期日志整理到长期记忆"""
        start_time = datetime.now()

        # 找出过期日志文件
        cutoff_time = datetime.now() - timedelta(days=days_threshold)
        old_logs = [
            f for f in self.log.daily_dir.glob("*.md")
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_time
        ]

        archived_items = []
        space_saved = 0

        for log_file in old_logs:
            # Archive to logs/archive
            archive_dir = self.log.log_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            archive_path = archive_dir / log_file.name
            shutil.move(str(log_file), str(archive_path))
            archived_items.append(str(archive_path))
            space_saved += log_file.stat().st_size

        time_taken = (datetime.now() - start_time).total_seconds()

        return ConsolidationResult(
            deleted_items=[],
            archived_items=archived_items,
            merged_items=[],
            space_saved=space_saved,
            time_taken=time_taken
        )

    def get_memory_health_report(self) -> Dict[str, Any]:
        """获取记忆健康报告"""
        snapshot = self.load_memory_snapshot()

        return {
            "overall_health": snapshot.health_score,
            "soul_completeness": snapshot.soul.completeness_score,
            "soul_size": snapshot.soul.total_size,
            "soul_valid_size": snapshot.soul.is_valid,
            "long_term_items": snapshot.long_term.total_items,
            "recent_log_count": len(snapshot.recent_logs),
            "last_updated": snapshot.long_term.last_updated,
            "snapshot_time": snapshot.snapshot_time,
            "recommendations": self._generate_recommendations(snapshot)
        }

    def _generate_recommendations(self, snapshot: MemorySnapshot) -> List[str]:
        """生成基于记忆状态的建议"""
        recommendations = []

        if not snapshot.soul.is_valid:
            recommendations.append(
                "人格层大小超出范围，建议调整至200-5000字"
            )

        if snapshot.soul.completeness_score < 0.75:
            recommendations.append(
                "人格层不完整，建议补充缺失的定义文件"
            )

        if snapshot.long_term.total_items < 10:
            recommendations.append(
                "长期记忆项较少，建议增加项目上下文和经验教训"
            )

        if len(snapshot.recent_logs) > 100:
            recommendations.append(
                "近期日志较多，建议执行记忆整合"
            )

        return recommendations