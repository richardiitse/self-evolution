#!/usr/bin/env python3
"""
Phase 2: Pattern Recognition

Identifies and analyzes patterns in code, behavior, and performance.

Key Concepts:
- Pattern Extraction: Extract recurring patterns from data
- Pattern Analysis: Analyze patterns for insights
- Pattern Matching: Match patterns against new data
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import hashlib


# ==================== Domain Classes ====================

@dataclass
class Pattern:
    """
    Represents a detected pattern.

    Attributes:
        - pattern_id: Unique identifier
        - name: Pattern name
        - pattern_type: Type of pattern (code, behavior, performance, etc.)
        - frequency: How often pattern occurs
        - confidence: Confidence in pattern detection (0.0 - 1.0)
        - description: Pattern description
        - examples: Example instances of pattern
        - metadata: Additional metadata
    """
    pattern_id: str
    name: str
    pattern_type: str
    frequency: int
    confidence: float
    description: str
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "pattern_type": self.pattern_type,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "description": self.description,
            "examples": self.examples,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PatternMatch:
    """
    Represents a pattern match result.

    Attributes:
        - pattern_id: Pattern that was matched
        - matched_data: Data that matched
        - match_score: Match confidence (0.0 - 1.0)
        - location: Where match occurred
    """
    pattern_id: str
    matched_data: Dict[str, Any]
    match_score: float
    location: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "matched_data": self.matched_data,
            "match_score": self.match_score,
            "location": self.location
        }


# ==================== Pattern Extractor ====================

class PatternExtractor:
    """
    Extract patterns from various data sources.

    Extraction Methods:
    - Frequency Analysis: Find frequently occurring items
    - Sequence Mining: Find recurring sequences
    - Clustering: Group similar items
    - Association Rules: Find correlated items
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir if storage_dir else Path.cwd() / ".strategies"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Extracted patterns
        self.patterns: Dict[str, Pattern] = {}

        # Minimum frequency threshold
        self.min_frequency = 3

    def extract_patterns(self, data: List[Dict[str, Any]]) -> List[Pattern]:
        """
        Extract patterns from structured data.

        Args:
            data: List of data items (e.g., code changes, behaviors)

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Extract frequency-based patterns
        freq_patterns = self._extract_frequency_patterns(data)
        patterns.extend(freq_patterns)

        # Extract sequence patterns
        seq_patterns = self._extract_sequence_patterns(data)
        patterns.extend(seq_patterns)

        # Extract attribute patterns
        attr_patterns = self._extract_attribute_patterns(data)
        patterns.extend(attr_patterns)

        # Store patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern
            self._save_pattern(pattern)

        return patterns

    def extract_from_logs(self, logs: List[str]) -> List[Pattern]:
        """
        Extract patterns from log entries.

        Args:
            logs: List of log strings

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Tokenize logs
        tokenized_logs = [self._tokenize_log(log) for log in logs]

        # Find recurring log patterns
        log_patterns = self._find_log_patterns(tokenized_logs)
        patterns.extend(log_patterns)

        # Find error patterns
        error_patterns = self._find_error_patterns(logs)
        patterns.extend(error_patterns)

        # Store patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern
            self._save_pattern(pattern)

        return patterns

    def _extract_frequency_patterns(self, data: List[Dict[str, Any]]) -> List[Pattern]:
        """Extract patterns based on item frequency."""
        patterns = []

        if not data:
            return patterns

        # Count occurrences of each item type
        type_counter = Counter()

        for item in data:
            item_type = item.get("type", "unknown")
            type_counter[item_type] += 1

        # Create patterns for frequent types
        for item_type, count in type_counter.items():
            if count >= self.min_frequency:
                pattern_id = self._generate_id(f"freq_{item_type}")

                # Confidence based on frequency
                confidence = min(1.0, count / len(data))

                # Get examples
                examples = [item for item in data if item.get("type") == item_type][:3]

                pattern = Pattern(
                    pattern_id=pattern_id,
                    name=f"Frequent {item_type}",
                    pattern_type="frequency",
                    frequency=count,
                    confidence=confidence,
                    description=f"{item_type} occurs {count} times",
                    examples=examples,
                    metadata={"item_type": item_type}
                )

                patterns.append(pattern)

        return patterns

    def _extract_sequence_patterns(self, data: List[Dict[str, Any]]) -> List[Pattern]:
        """Extract recurring sequences from ordered data."""
        patterns = []

        if len(data) < 2:
            return patterns

        # Find sequences of length 2-3
        for seq_len in range(2, 4):
            sequences = self._find_sequences(data, seq_len)

            # Count sequence frequencies
            seq_counter = Counter(sequences)

            # Create patterns for frequent sequences
            for sequence, count in seq_counter.items():
                if count >= self.min_frequency:
                    seq_str = " -> ".join(sequence)
                    pattern_id = self._generate_id(f"seq_{seq_len}_{hash(seq_str) % 1000}")

                    confidence = min(1.0, count / len(data))

                    pattern = Pattern(
                        pattern_id=pattern_id,
                        name=f"Sequence: {seq_str}",
                        pattern_type="sequence",
                        frequency=count,
                        confidence=confidence,
                        description=f"Sequence '{seq_str}' occurs {count} times",
                        metadata={"sequence": sequence, "length": seq_len}
                    )

                    patterns.append(pattern)

        return patterns

    def _extract_attribute_patterns(self, data: List[Dict[str, Any]]) -> List[Pattern]:
        """Extract patterns based on attribute values."""
        patterns = []

        if not data:
            return patterns

        # Group by attributes
        attr_values: Dict[str, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))

        for item in data:
            for key, value in item.items():
                if key != "type":  # Skip type (already handled)
                    attr_values[key][value] += 1

        # Create patterns for frequent attribute values
        for attr, values in attr_values.items():
            for value, count in values.items():
                if count >= self.min_frequency:
                    pattern_id = self._generate_id(f"attr_{attr}_{hash(str(value)) % 1000}")

                    confidence = min(1.0, count / len(data))

                    pattern = Pattern(
                        pattern_id=pattern_id,
                        name=f"Attribute: {attr}={value}",
                        pattern_type="attribute",
                        frequency=count,
                        confidence=confidence,
                        description=f"{attr}={value} occurs {count} times",
                        metadata={"attribute": attr, "value": str(value)}
                    )

                    patterns.append(pattern)

        return patterns

    def _find_sequences(self, data: List[Dict[str, Any]], length: int) -> List[Tuple]:
        """Find all sequences of given length."""
        sequences = []

        for i in range(len(data) - length + 1):
            sequence = tuple(data[j].get("type", "unknown") for j in range(i, i + length))
            sequences.append(sequence)

        return sequences

    def _tokenize_log(self, log: str) -> List[str]:
        """Tokenize log entry."""
        # Simple tokenization by splitting on whitespace and punctuation
        tokens = re.findall(r'\w+', log.lower())
        return tokens

    def _find_log_patterns(self, tokenized_logs: List[List[str]]) -> List[Pattern]:
        """Find patterns in tokenized logs."""
        patterns = []

        # Find frequent n-grams
        for n in range(2, 5):  # 2-4 grams
            ngrams = []

            for tokens in tokenized_logs:
                if len(tokens) >= n:
                    for i in range(len(tokens) - n + 1):
                        ngram = tuple(tokens[i:i+n])
                        ngrams.append(ngram)

            # Count n-grams
            ngram_counter = Counter(ngrams)

            # Create patterns for frequent n-grams
            for ngram, count in ngram_counter.items():
                if count >= self.min_frequency:
                    ngram_str = " ".join(ngram)
                    pattern_id = self._generate_id(f"log_ngram_{hash(ngram_str) % 1000}")

                    confidence = min(1.0, count / len(tokenized_logs))

                    pattern = Pattern(
                        pattern_id=pattern_id,
                        name=f"Log Pattern: {ngram_str}",
                        pattern_type="log",
                        frequency=count,
                        confidence=confidence,
                        description=f"Log pattern '{ngram_str}' occurs {count} times",
                        metadata={"ngram": ngram, "length": n}
                    )

                    patterns.append(pattern)

        return patterns

    def _find_error_patterns(self, logs: List[str]) -> List[Pattern]:
        """Find error patterns in logs."""
        patterns = []

        # Find error logs
        error_logs = [log for log in logs if any(word in log.lower() for word in ["error", "exception", "fail"])]

        if len(error_logs) < self.min_frequency:
            return patterns

        # Extract error types
        error_types = []
        for log in error_logs:
            # Simple extraction: find word after "error" or "exception"
            match = re.search(r'(error|exception|fail)[\s:]+(\w+)', log.lower())
            if match:
                error_types.append(match.group(2))
            else:
                error_types.append("unknown")

        # Count error types
        error_counter = Counter(error_types)

        # Create patterns for frequent errors
        for error_type, count in error_counter.items():
            if count >= 2:  # Lower threshold for errors
                pattern_id = self._generate_id(f"error_{error_type}")

                confidence = min(1.0, count / len(error_logs))

                pattern = Pattern(
                    pattern_id=pattern_id,
                    name=f"Error Pattern: {error_type}",
                    pattern_type="error",
                    frequency=count,
                    confidence=confidence,
                    description=f"Error '{error_type}' occurs {count} times",
                    metadata={"error_type": error_type}
                )

                patterns.append(pattern)

        return patterns

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{prefix}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]

    def _save_pattern(self, pattern: Pattern):
        """Save pattern to storage."""
        pattern_file = self.storage_dir / f"pattern_{pattern.pattern_id}.json"
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(pattern.to_dict(), f, indent=2)


# ==================== Pattern Analyzer ====================

class PatternAnalyzer:
    """
    Analyze patterns for insights.

    Analysis Methods:
    - Similarity: Find similar patterns
    - Correlation: Find correlated patterns
    - Trend: Analyze pattern trends over time
    - Anomaly: Detect anomalous patterns
    """

    def __init__(self):
        self.similarity_threshold = 0.7

    def analyze_pattern(self, pattern: Pattern) -> Dict[str, Any]:
        """
        Analyze a single pattern.

        Args:
            pattern: Pattern to analyze

        Returns:
            Analysis results
        """
        analysis = {
            "pattern_id": pattern.pattern_id,
            "name": pattern.name,
            "type": pattern.pattern_type,
            "frequency": pattern.frequency,
            "confidence": pattern.confidence,
            "significance": self._calculate_significance(pattern),
            "stability": self._calculate_stability(pattern),
            "recommendations": self._generate_recommendations(pattern)
        }

        return analysis

    def find_similar_patterns(
        self,
        pattern: Pattern,
        patterns: List[Pattern]
    ) -> List[Tuple[Pattern, float]]:
        """
        Find patterns similar to the given pattern.

        Args:
            pattern: Pattern to compare against
            patterns: List of patterns to search

        Returns:
            List of (pattern, similarity) tuples
        """
        similar = []

        for other in patterns:
            if other.pattern_id == pattern.pattern_id:
                continue

            similarity = self._calculate_similarity(pattern, other)

            if similarity >= self.similarity_threshold:
                similar.append((other, similarity))

        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)

        return similar

    def analyze_pattern_relationships(
        self,
        patterns: List[Pattern]
    ) -> Dict[str, List[str]]:
        """
        Analyze relationships between patterns.

        Args:
            patterns: List of patterns to analyze

        Returns:
            Dictionary mapping pattern_id to related pattern_ids
        """
        relationships = {}

        for pattern in patterns:
            similar = self.find_similar_patterns(pattern, patterns)
            related_ids = [p.pattern_id for p, _ in similar]
            relationships[pattern.pattern_id] = related_ids

        return relationships

    def _calculate_significance(self, pattern: Pattern) -> float:
        """Calculate pattern significance."""
        # Significance = frequency * confidence
        return min(1.0, pattern.frequency * pattern.confidence / 10.0)

    def _calculate_stability(self, pattern: Pattern) -> float:
        """Calculate pattern stability."""
        # Higher confidence = more stable
        return pattern.confidence

    def _generate_recommendations(self, pattern: Pattern) -> List[str]:
        """Generate recommendations based on pattern."""
        recommendations = []

        if pattern.pattern_type == "error":
            recommendations.append(f"Investigate and fix error pattern: {pattern.name}")
        elif pattern.pattern_type == "frequency":
            if pattern.frequency > 10:
                recommendations.append(f"Consider optimizing frequent pattern: {pattern.name}")
        elif pattern.pattern_type == "sequence":
            recommendations.append(f"Automate sequence: {pattern.name}")

        if pattern.confidence < 0.5:
            recommendations.append("Low confidence - gather more data")

        return recommendations

    def _calculate_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """Calculate similarity between two patterns."""
        # Same type = higher similarity
        type_similarity = 1.0 if pattern1.pattern_type == pattern2.pattern_type else 0.5

        # Frequency similarity (normalized)
        max_freq = max(pattern1.frequency, pattern2.frequency)
        freq_similarity = 1.0 - abs(pattern1.frequency - pattern2.frequency) / (max_freq + 1)

        # Combined similarity
        similarity = 0.5 * type_similarity + 0.5 * freq_similarity

        return similarity


# ==================== Pattern Matcher ====================

class PatternMatcher:
    """
    Match patterns against data.

    Matching Methods:
    - Exact Match: Exact pattern match
    - Fuzzy Match: Approximate pattern match
    - Semantic Match: Meaning-based match
    """

    def __init__(self):
        self.match_threshold = 0.5

    def match_pattern(
        self,
        data: Dict[str, Any],
        pattern: Pattern
    ) -> bool:
        """
        Check if data matches a pattern.

        Args:
            data: Data to check
            pattern: Pattern to match against

        Returns:
            True if data matches pattern
        """
        if pattern.pattern_type == "frequency":
            return self._match_frequency_pattern(data, pattern)
        elif pattern.pattern_type == "sequence":
            return self._match_sequence_pattern(data, pattern)
        elif pattern.pattern_type == "attribute":
            return self._match_attribute_pattern(data, pattern)
        elif pattern.pattern_type == "error":
            return self._match_error_pattern(data, pattern)
        else:
            return False

    def find_matches(
        self,
        data: List[Dict[str, Any]],
        patterns: List[Pattern]
    ) -> List[PatternMatch]:
        """
        Find all pattern matches in data.

        Args:
            data: Data to search
            patterns: Patterns to match

        Returns:
            List of pattern matches
        """
        matches = []

        for item in data:
            for pattern in patterns:
                if self.match_pattern(item, pattern):
                    match_score = self._calculate_match_score(item, pattern)

                    match = PatternMatch(
                        pattern_id=pattern.pattern_id,
                        matched_data=item,
                        match_score=match_score,
                        location=item.get("location", "unknown")
                    )

                    matches.append(match)

        return matches

    def _match_frequency_pattern(self, data: Dict[str, Any], pattern: Pattern) -> bool:
        """Match frequency-based pattern."""
        item_type = data.get("type")
        pattern_type = pattern.metadata.get("item_type")

        return item_type == pattern_type

    def _match_sequence_pattern(self, data: Dict[str, Any], pattern: Pattern) -> bool:
        """Match sequence pattern."""
        # For single item, check if it's part of the sequence
        item_type = data.get("type")
        sequence = pattern.metadata.get("sequence", [])

        return item_type in sequence

    def _match_attribute_pattern(self, data: Dict[str, Any], pattern: Pattern) -> bool:
        """Match attribute pattern."""
        attr = pattern.metadata.get("attribute")
        value = pattern.metadata.get("value")

        return str(data.get(attr, "")) == value

    def _match_error_pattern(self, data: Dict[str, Any], pattern: Pattern) -> bool:
        """Match error pattern."""
        error_type = pattern.metadata.get("error_type")
        data_str = str(data).lower()

        return error_type in data_str

    def _calculate_match_score(self, data: Dict[str, Any], pattern: Pattern) -> float:
        """Calculate match confidence score."""
        # Base score on pattern confidence
        base_score = pattern.confidence

        # Adjust based on match quality
        if pattern.pattern_type == "frequency":
            # Exact type match = high score
            return base_score * 0.9
        elif pattern.pattern_type == "attribute":
            # Exact value match = high score
            return base_score * 0.95
        else:
            return base_score * 0.8


# ==================== Main ====================

def main():
    """Simple demo of Pattern Recognition components."""
    print("=" * 70)
    print("🔍 Pattern Recognition - Demo")
    print("=" * 70)
    print()

    # Pattern Extractor
    print("📊 Extracting patterns...")
    extractor = PatternExtractor()

    # Sample data
    data = [
        {"type": "code_change", "language": "python", "file": "test.py"},
        {"type": "code_change", "language": "python", "file": "main.py"},
        {"type": "code_change", "language": "python", "file": "utils.py"},
        {"type": "test_run", "status": "passed"},
        {"type": "test_run", "status": "passed"},
        {"type": "deployment", "env": "production"}
    ]

    patterns = extractor.extract_patterns(data)
    print(f"  Found {len(patterns)} patterns")
    for pattern in patterns[:3]:
        print(f"    - {pattern.name}: frequency={pattern.frequency}, confidence={pattern.confidence:.2f}")

    # Pattern Analyzer
    print("\n🔬 Analyzing patterns...")
    analyzer = PatternAnalyzer()

    if patterns:
        pattern = patterns[0]
        analysis = analyzer.analyze_pattern(pattern)
        print(f"  Pattern: {pattern.name}")
        print(f"    Significance: {analysis['significance']:.2f}")
        print(f"    Stability: {analysis['stability']:.2f}")

        similar = analyzer.find_similar_patterns(pattern, patterns)
        if similar:
            print(f"    Similar patterns: {len(similar)}")

    # Pattern Matcher
    print("\n🎯 Matching patterns...")
    matcher = PatternMatcher()

    new_data = [
        {"type": "code_change", "language": "python", "file": "new.py"},
        {"type": "test_run", "status": "failed"}
    ]

    matches = matcher.find_matches(new_data, patterns)
    print(f"  Found {len(matches)} matches")
    for match in matches[:3]:
        print(f"    - Pattern {match.pattern_id}: score={match.match_score:.2f}")

    print("\n" + "=" * 70)
    print("✅ Pattern Recognition demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
