"""
Evolution Log - Complete audit tracking for safe self-modification.

Based on MIRI corrigibility principles: all modifications must be logged,
traceable, and auditable to maintain transparency and enable rollback.
"""

import json
import os
import shutil
import gzip
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class LogEntry:
    """Single log entry in the evolution audit trail."""
    entry_id: str
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, CRITICAL
    event_type: str  # MODIFICATION, VALIDATION, ROLLBACK, ANALYSIS
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    safety_check_passed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create log entry from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class EvolutionPattern:
    """Pattern detected in evolution logs."""
    pattern_type: str  # RECURRENT_FAILURE, SAFETY_DEGRADATION, RESOURCE_SHORTAGE, etc.
    frequency: int
    first_occurrence: datetime
    last_occurrence: datetime
    affected_components: List[str]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str


@dataclass
class EvolutionAnalysis:
    """Analysis result of evolution logs."""
    total_entries: int
    time_span: tuple[datetime, datetime]
    event_distribution: Dict[str, int]
    success_rate: float
    safety_check_pass_rate: float
    patterns: List[EvolutionPattern]
    critical_issues: List[str]
    recommendations: List[str]


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    confidence: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvolutionLog:
    """
    Main logging system for evolution tracking.

    Maintains complete audit trail of all self-modification attempts,
    safety checks, and system state changes.
    """

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize evolution log.

        Args:
            log_dir: Directory to store logs (default: .evolution/logs/)
        """
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), '.evolution', 'logs')

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.current_log_file = self.log_dir / f"evolution_{datetime.now().strftime('%Y%m%d')}.log"
        self.entries: List[LogEntry] = []

    def log(self,
            level: str,
            event_type: str,
            message: str,
            data: Optional[Dict[str, Any]] = None,
            safety_check: bool = True,
            metadata: Optional[Dict[str, Any]] = None) -> LogEntry:
        """
        Create and store a log entry.

        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            event_type: Type of event being logged
            message: Human-readable message
            data: Event-specific data
            safety_check: Whether safety checks passed
            metadata: Additional metadata

        Returns:
            Created LogEntry
        """
        entry_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.entries):06d}"

        entry = LogEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            level=level.upper(),
            event_type=event_type.upper(),
            message=message,
            data=data or {},
            safety_check_passed=safety_check,
            metadata=metadata or {}
        )

        self.entries.append(entry)
        self._write_entry(entry)

        return entry

    def _write_entry(self, entry: LogEntry) -> None:
        """Write log entry to file."""
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False)
            f.write('\n')

    def get_entries(self,
                   filters: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[LogEntry]:
        """
        Retrieve log entries with optional filtering.

        Args:
            filters: Filter criteria (level, event_type, start_time, end_time, etc.)
            limit: Maximum number of entries to return

        Returns:
            List of matching log entries
        """
        entries = self.entries.copy()

        if filters:
            if 'level' in filters:
                entries = [e for e in entries if e.level == filters['level'].upper()]
            if 'event_type' in filters:
                entries = [e for e in entries if e.event_type == filters['event_type'].upper()]
            if 'start_time' in filters:
                start_time = filters['start_time']
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                entries = [e for e in entries if e.timestamp >= start_time]
            if 'end_time' in filters:
                end_time = filters['end_time']
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                entries = [e for e in entries if e.timestamp <= end_time]
            if 'safety_check_passed' in filters:
                entries = [e for e in entries if e.safety_check_passed == filters['safety_check_passed']]

        if limit:
            entries = entries[:limit]

        return entries

    def load_from_file(self, log_file: str) -> int:
        """
        Load entries from a log file.

        Args:
            log_file: Path to log file

        Returns:
            Number of entries loaded
        """
        count = 0
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = LogEntry.from_dict(data)
                        self.entries.append(entry)
                        count += 1
        except FileNotFoundError:
            pass

        return count

    def load_all_logs(self) -> int:
        """Load all log files from the log directory."""
        total_count = 0
        for log_file in self.log_dir.glob("evolution_*.log"):
            total_count += self.load_from_file(str(log_file))
        return total_count

    def clear_old_entries(self, days: int = 30) -> int:
        """
        Clear entries older than specified days from memory.

        Args:
            days: Number of days to keep

        Returns:
            Number of entries cleared
        """
        cutoff = datetime.now().timestamp() - (days * 86400)
        old_count = len(self.entries)
        self.entries = [e for e in self.entries if e.timestamp.timestamp() > cutoff]
        return old_count - len(self.entries)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged events."""
        if not self.entries:
            return {
                'total_entries': 0,
                'by_level': {},
                'by_event_type': {},
                'safety_pass_rate': 0.0,
                'time_span': None
            }

        by_level = {}
        by_event_type = {}
        safety_passes = sum(1 for e in self.entries if e.safety_check_passed)

        for entry in self.entries:
            by_level[entry.level] = by_level.get(entry.level, 0) + 1
            by_event_type[entry.event_type] = by_event_type.get(entry.event_type, 0) + 1

        timestamps = [e.timestamp for e in self.entries]

        return {
            'total_entries': len(self.entries),
            'by_level': by_level,
            'by_event_type': by_event_type,
            'safety_pass_rate': safety_passes / len(self.entries) if self.entries else 0.0,
            'time_span': (min(timestamps), max(timestamps)) if timestamps else None
        }


class LogAnalyzer:
    """
    Analyzes evolution logs to detect patterns and issues.

    Based on MIRI research: pattern detection is crucial for predicting
    and preventing unsafe behaviors before they manifest.
    """

    def __init__(self, log: EvolutionLog):
        """
        Initialize log analyzer.

        Args:
            log: EvolutionLog instance to analyze
        """
        self.log = log

    def analyze_log(self, log_path: Optional[str] = None) -> EvolutionAnalysis:
        """
        Perform comprehensive analysis of evolution logs.

        Args:
            log_path: Optional specific log file to analyze

        Returns:
            EvolutionAnalysis with findings
        """
        if log_path:
            self.log.load_from_file(log_path)
        else:
            self.log.load_all_logs()

        entries = self.log.entries

        if not entries:
            return EvolutionAnalysis(
                total_entries=0,
                time_span=(datetime.now(), datetime.now()),
                event_distribution={},
                success_rate=0.0,
                safety_check_pass_rate=0.0,
                patterns=[],
                critical_issues=[],
                recommendations=[]
            )

        timestamps = [e.timestamp for e in entries]
        time_span = (min(timestamps), max(timestamps))

        event_distribution = {}
        safety_passes = 0
        successful_events = 0

        for entry in entries:
            event_distribution[entry.event_type] = event_distribution.get(entry.event_type, 0) + 1
            if entry.safety_check_passed:
                safety_passes += 1
            if entry.level != 'ERROR' and entry.level != 'CRITICAL':
                successful_events += 1

        patterns = self.extract_patterns(log_path)

        critical_issues = self._identify_critical_issues(entries)
        recommendations = self._generate_recommendations(patterns, critical_issues)

        return EvolutionAnalysis(
            total_entries=len(entries),
            time_span=time_span,
            event_distribution=event_distribution,
            success_rate=successful_events / len(entries) if entries else 0.0,
            safety_check_pass_rate=safety_passes / len(entries) if entries else 0.0,
            patterns=patterns,
            critical_issues=critical_issues,
            recommendations=recommendations
        )

    def extract_patterns(self, log_path: Optional[str] = None) -> List[EvolutionPattern]:
        """
        Extract patterns from evolution logs.

        Args:
            log_path: Optional specific log file to analyze

        Returns:
            List of detected patterns
        """
        entries = self.log.entries
        patterns = []

        if not entries:
            return patterns

        # Group entries by event type and analyze
        event_groups: Dict[str, List[LogEntry]] = {}
        for entry in entries:
            if entry.event_type not in event_groups:
                event_groups[entry.event_type] = []
            event_groups[entry.event_type].append(entry)

        # Detect recurrent failures
        for event_type, group_entries in event_groups.items():
            failures = [e for e in group_entries if e.level in ('ERROR', 'CRITICAL')]

            if len(failures) >= 3:  # Threshold for pattern detection
                timestamps = [e.timestamp for e in failures]
                affected_components = list(set([e.data.get('component', 'unknown') for e in failures]))

                severity = 'LOW'
                if len(failures) >= 5:
                    severity = 'MEDIUM'
                if len(failures) >= 10:
                    severity = 'HIGH'
                if len(failures) >= 20 or any(e.level == 'CRITICAL' for e in failures):
                    severity = 'CRITICAL'

                patterns.append(EvolutionPattern(
                    pattern_type='RECURRENT_FAILURE',
                    frequency=len(failures),
                    first_occurrence=min(timestamps),
                    last_occurrence=max(timestamps),
                    affected_components=affected_components,
                    severity=severity,
                    description=f"Recurrent {event_type} failures ({len(failures)} occurrences)"
                ))

        # Detect safety degradation
        recent_entries = [e for e in entries if (datetime.now() - e.timestamp).days <= 7]
        if recent_entries:
            safety_failures = [e for e in recent_entries if not e.safety_check_passed]
            if len(safety_failures) >= len(recent_entries) * 0.1:  # 10% threshold
                patterns.append(EvolutionPattern(
                    pattern_type='SAFETY_DEGRADATION',
                    frequency=len(safety_failures),
                    first_occurrence=min(e.timestamp for e in safety_failures),
                    last_occurrence=max(e.timestamp for e in safety_failures),
                    affected_components=['safety_validator'],
                    severity='HIGH',
                    description=f"Safety check failure rate: {len(safety_failures)/len(recent_entries)*100:.1f}%"
                ))

        return patterns

    def _identify_critical_issues(self, entries: List[LogEntry]) -> List[str]:
        """Identify critical issues from log entries."""
        issues = []

        # Check for CRITICAL level entries
        critical_entries = [e for e in entries if e.level == 'CRITICAL']
        if critical_entries:
            issues.append(f"Found {len(critical_entries)} critical events requiring immediate attention")

        # Check for safety check failures
        safety_failures = [e for e in entries if not e.safety_check_passed]
        if len(safety_failures) > len(entries) * 0.05:  # 5% threshold
            issues.append(f"Safety check failure rate ({len(safety_failures)/len(entries)*100:.1f}%) exceeds threshold")

        # Check for error clusters
        recent_errors = [e for e in entries if e.level == 'ERROR' and (datetime.now() - e.timestamp).hours <= 24]
        if len(recent_errors) >= 10:
            issues.append(f"High error rate in last 24 hours: {len(recent_errors)} errors")

        return issues

    def _generate_recommendations(self,
                                  patterns: List[EvolutionPattern],
                                  critical_issues: List[str]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        for pattern in patterns:
            if pattern.pattern_type == 'RECURRENT_FAILURE':
                recommendations.append(
                    f"Investigate and fix recurrent failures in {', '.join(pattern.affected_components)}"
                )
            elif pattern.pattern_type == 'SAFETY_DEGRADATION':
                recommendations.append("Review and strengthen safety validation procedures")

        if critical_issues:
            recommendations.append("Address critical issues immediately before continuing evolution")

        if not patterns and not critical_issues:
            recommendations.append("System operating normally, continue monitoring")

        return recommendations


class LogArchiver:
    """
    Archives old evolution logs to maintain system performance.

    Based on MIRI principle: maintain complete audit trail while ensuring
    system efficiency through intelligent log management.
    """

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize log archiver.

        Args:
            log_dir: Directory containing logs to archive
        """
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), '.evolution', 'logs')

        self.log_dir = Path(log_dir)
        self.archive_dir = self.log_dir / 'archive'
        self.archive_dir.mkdir(exist_ok=True)

    def archive_old_logs(self, days_threshold: int = 30) -> List[str]:
        """
        Archive log files older than threshold.

        Args:
            days_threshold: Age in days after which logs are archived

        Returns:
            List of archived file paths
        """
        cutoff_time = datetime.now().timestamp() - (days_threshold * 86400)
        archived = []

        for log_file in self.log_dir.glob("evolution_*.log"):
            if log_file.is_file():
                file_mtime = log_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    archive_path = self.archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    archived.append(str(archive_path))

        return archived

    def compress_logs(self, log_files: Optional[List[str]] = None) -> List[str]:
        """
        Compress log files to save space.

        Args:
            log_files: List of log files to compress (default: all in archive)

        Returns:
            List of compressed file paths
        """
        if log_files is None:
            log_files = [str(f) for f in self.archive_dir.glob("*.log")]

        compressed = []

        for log_file in log_files:
            log_path = Path(log_file)
            if log_path.exists() and not log_path.suffix == '.gz':
                gzip_path = log_path.with_suffix(log_path.suffix + '.gz')

                with open(log_path, 'rb') as f_in:
                    with gzip.open(gzip_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                log_path.unlink()
                compressed.append(str(gzip_path))

        return compressed

    def cleanup_archive(self, days_threshold: int = 90) -> int:
        """
        Remove very old compressed logs from archive.

        Args:
            days_threshold: Age in days after which compressed logs are removed

        Returns:
            Number of files removed
        """
        cutoff_time = datetime.now().timestamp() - (days_threshold * 86400)
        removed = 0

        for log_file in self.archive_dir.glob("*.gz"):
            if log_file.is_file():
                file_mtime = log_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    log_file.unlink()
                    removed += 1

        return removed
