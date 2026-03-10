"""
Cross-Skill Transfer

Enables transfer of patterns between skills and domains.

Components:
- PatternTransfer - Transfer patterns between skills
- SkillRegistry - Register and manage skills
- SimilarityScorer - Score pattern similarity
- TransferEvaluator - Evaluate transfer suitability
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import os


@dataclass
class Pattern:
    """
    Represents a transferable pattern.
    
    Attributes:
        - id: Pattern ID
        - source_skill: Source skill name
        - pattern_type: Pattern type (code, configuration, etc.)
        - description: Pattern description
        - implementation: Pattern implementation (code, config, etc.)
        - success_count: How many times pattern succeeded
        - failure_count: How many times pattern failed
        - context: Additional context
        - last_used: Last time pattern was used
        - metadata: Additional metadata
    """
    id: str
    source_skill: str
    pattern_type: str
    description: str
    implementation: Any  # Could be code, config, etc.
    success_count: int
    failure_count: int
    context: Dict[str, Any]
    last_used: datetime
    metadata: Dict[str, Any]


@dataclass
class TransferSuitability:
    """
    Represents transfer suitability result.
    
    Attributes:
        - pattern: The pattern being transferred
        - target_skill: Target skill name
        - similarity_score: Similarity score (0.0 - 1.0)
        - complexity_score: Complexity score (0.0 - 1.0)
        - risk_score: Risk score (0.0 - 1.0)
        - transfer_score: Overall transfer score (0.0 - 1.0)
        - confidence: Confidence in transfer (0.0 - 1.0)
        - recommendation: Transfer recommendation (transfer, adapt, reject)
    """
    pattern: Pattern
    target_skill: str
    similarity_score: float
    complexity_score: float
    risk_score: float
    transfer_score: float
    confidence: float
    recommendation: str  # "transfer", "adapt", "reject"


@dataclass
class TransferResult:
    """
    Represents a pattern transfer result.
    
    Attributes:
        - pattern_id: Pattern ID
        - source_skill: Source skill name
        - target_skill: Target skill name
        - success: Whether transfer succeeded
        - adapted: Whether pattern was adapted
        - adaptation_details: Details of adaptation (if any)
        - timestamp: When transfer was attempted
        - feedback: Transfer feedback
    """
    pattern_id: str
    source_skill: str
    target_skill: str
    success: bool
    adapted: bool
    adaptation_details: str
    timestamp: datetime
    feedback: str


class SimilarityScorer:
    """
    Score pattern similarity for transfer evaluation.
    
    Similarity Metrics:
    - Type similarity (pattern types match)
    - Context similarity (contexts are similar)
    - Implementation similarity (implementations are similar)
    - Metadata similarity (metadata matches)
    """
    
    def __init__(self):
        self.type_similarity_weight = 0.3
        self.context_similarity_weight = 0.2
        self.implementation_similarity_weight = 0.3
        self.metadata_similarity_weight = 0.2
    
    def score_type_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """
        Score type similarity.
        
        Returns: 1.0 if types match, 0.0 otherwise
        """
        if pattern1.pattern_type == pattern2.pattern_type:
            return 1.0
        else:
            return 0.0
    
    def score_context_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """
        Score context similarity.
        
        Returns: 1.0 if contexts have overlapping keys, 0.0 otherwise
        """
        context1 = pattern1.context or {}
        context2 = pattern2.context or {}
        
        if not context1 or not context2:
            return 0.0
        
        # Count overlapping keys
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        overlap = len(keys1.intersection(keys2))
        
        # Calculate similarity
        total_keys = len(keys1.union(keys2))
        if total_keys == 0:
            return 0.0
        
        return overlap / total_keys
    
    def score_implementation_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """
        Score implementation similarity.
        
        Returns: 0.0 - 1.0 based on string comparison
        """
        impl1 = pattern1.implementation or ""
        impl2 = pattern2.implementation or ""
        
        # If both are strings, compare them
        if isinstance(impl1, str) and isinstance(impl2, str):
            if impl1 == impl2:
                return 1.0
            else:
                # Simple similarity based on common characters
                common_chars = set(impl1).intersection(set(impl2))
                total_chars = len(set(impl1).union(set(impl2)))
                
                if total_chars == 0:
                    return 0.0
                
                return len(common_chars) / total_chars
        else:
            # Different types - can't compare
            return 0.0
    
    def score_metadata_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """
        Score metadata similarity.
        
        Returns: 1.0 if all metadata matches, 0.0 otherwise
        """
        metadata1 = pattern1.metadata or {}
        metadata2 = pattern2.metadata or {}
        
        if not metadata1 or not metadata2:
            return 0.0
        
        # Count matching metadata keys
        matching_keys = []
        for key in metadata1.keys():
            if key in metadata2 and metadata1[key] == metadata2[key]:
                matching_keys.append(key)
        
        if not matching_keys:
            return 0.0
        
        total_keys = len(metadata1.keys())
        return len(matching_keys) / total_keys
    
    def calculate_overall_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """
        Calculate overall pattern similarity.
        
        Args:
            pattern1: First pattern
            pattern2: Second pattern
        
        Returns:
            Overall similarity score (0.0 - 1.0)
        """
        type_sim = self.score_type_similarity(pattern1, pattern2)
        context_sim = self.score_context_similarity(pattern1, pattern2)
        impl_sim = self.score_implementation_similarity(pattern1, pattern2)
        metadata_sim = self.score_metadata_similarity(pattern1, pattern2)
        
        # Calculate weighted score
        similarity = (
            self.type_similarity_weight * type_sim +
            self.context_similarity_weight * context_sim +
            self.implementation_similarity_weight * impl_sim +
            self.metadata_similarity_weight * metadata_sim
        )
        
        return similarity


class TransferEvaluator:
    """
    Evaluate transfer suitability and recommend transfers.
    
    Evaluation Criteria:
    - Similarity score (higher = better)
    - Complexity score (lower = better)
    - Risk score (lower = better)
    - Success rate (higher = better)
    - Transfer score (weighted combination)
    """
    
    def __init__(self, similarity_scorer: SimilarityScorer = None):
        self.similarity_scorer = similarity_scorer or SimilarityScorer()
        
        self.similarity_weight = 0.4
        self.complexity_weight = 0.2
        self.risk_weight = 0.3
        self.success_rate_weight = 0.1
    
    def calculate_success_rate(self, pattern: Pattern) -> float:
        """
        Calculate pattern success rate.
        
        Returns: Success rate (0.0 - 1.0)
        """
        total = pattern.success_count + pattern.failure_count
        if total == 0:
            return 0.5  # Neutral
        
        return pattern.success_count / total
    
    def calculate_risk_score(self, pattern: Pattern) -> float:
        """
        Calculate pattern risk score.
        
        Returns: Risk score (0.0 - 1.0)
        """
        # Risk based on failure rate
        failure_rate = self.calculate_success_rate(pattern)
        
        # High failure rate = high risk
        if failure_rate < 0.5:
            return 0.2  # Low risk
        elif failure_rate < 0.8:
            return 0.5  # Medium risk
        else:
            return 0.8  # High risk
    
    def calculate_complexity_score(self, pattern: Pattern) -> float:
        """
        Calculate pattern complexity score.
        
        Returns: Complexity score (0.0 - 1.0)
        """
        # Complexity based on implementation size
        impl = pattern.implementation
        
        if isinstance(impl, str):
            # Simple: length-based complexity
            length = len(impl)
            
            if length < 100:
                return 0.2  # Low complexity
            elif length < 500:
                return 0.5  # Medium complexity
            else:
                return 0.8  # High complexity
        else:
            # Non-string implementation - assume medium complexity
            return 0.5
    
    def calculate_transfer_score(self, pattern: Pattern, target_skill: str,
                                similarity: float, risk: float, complexity: float) -> float:
        """
        Calculate overall transfer score.
        
        Args:
            pattern: Pattern being transferred
            target_skill: Target skill name
            similarity: Similarity score (0.0 - 1.0)
            risk: Risk score (0.0 - 1.0)
            complexity: Complexity score (0.0 - 1.0)
        
        Returns:
            Transfer score (0.0 - 1.0)
        """
        # Calculate weighted score
        transfer_score = (
            self.similarity_weight * similarity -
            self.complexity_weight * complexity -
            self.risk_weight * risk +
            self.success_rate_weight * self.calculate_success_rate(pattern)
        )
        
        # Clamp to 0.0 - 1.0
        return max(0.0, min(1.0, transfer_score))
    
    def evaluate_transfer(self, pattern: Pattern, target_skill: str,
                        source_skill: str) -> TransferSuitability:
        """
        Evaluate transfer suitability.
        
        Args:
            pattern: Pattern being transferred
            target_skill: Target skill name
            source_skill: Source skill name
        
        Returns:
            TransferSuitability with evaluation results
        """
        # Calculate success rate
        success_rate = self.calculate_success_rate(pattern)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(pattern)
        
        # Calculate complexity score
        complexity_score = self.calculate_complexity_score(pattern)
        
        # Calculate similarity (requires target skill patterns)
        # For now, assume high similarity if types match
        if pattern.pattern_type in ["code", "config", "data"]:
            similarity = 0.7
        else:
            similarity = 0.5
        
        # Calculate transfer score
        transfer_score = self.calculate_transfer_score(
            pattern, target_skill, similarity, risk_score, complexity_score
        )
        
        # Calculate confidence
        confidence = min(success_rate, similarity)
        
        # Determine recommendation
        if transfer_score > 0.6 and confidence > 0.6:
            recommendation = "transfer"
        elif transfer_score > 0.4:
            recommendation = "adapt"
        else:
            recommendation = "reject"
        
        return TransferSuitability(
            pattern=pattern,
            target_skill=target_skill,
            similarity_score=similarity,
            complexity_score=complexity_score,
            risk_score=risk_score,
            transfer_score=transfer_score,
            confidence=confidence,
            recommendation=recommendation
        )


class SkillRegistry:
    """
    Register and manage skills for pattern transfer.
    
    Registry Features:
    - Register skills with metadata
    - Register patterns for skills
    - Get skill patterns
    - Find compatible skills
    - Record transfers
    - Track transfer success
    """
    
    def __init__(self, registry_dir: Optional[Path] = None):
        self.registry_dir = registry_dir if registry_dir else Path.home() / ".clawhub" / "skills"
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize registry
        self.skills = {}
        self.patterns = {}
        self.transfers = {}
        self.compatibility_matrix = {}
        
        self.load_registry()
    
    def load_registry(self):
        """Load skill registry from file."""
        registry_file = self.registry_dir / "skill_registry.json"
        
        if not registry_file.exists():
            self.save_registry()
            return
        
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.skills = data.get("skills", {})
                self.patterns = data.get("patterns", {})
                self.transfers = data.get("transfers", {})
                self.compatibility_matrix = data.get("compatibility_matrix", {})
        except Exception as e:
            print(f"Warning: Could not load registry: {e}")
    
    def save_registry(self):
        """Save skill registry to file."""
        registry_file = self.registry_dir / "skill_registry.json"
        
        try:
            data = {
                "skills": self.skills,
                "patterns": self.patterns,
                "transfers": self.transfers,
                "compatibility_matrix": self.compatibility_matrix,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save registry: {e}")
    
    def register_skill(self, skill_id: str, metadata: Dict[str, Any]):
        """
        Register a skill with metadata.
        
        Args:
            skill_id: Skill identifier
            metadata: Skill metadata (type, description, etc.)
        """
        self.skills[skill_id] = {
            "id": skill_id,
            "metadata": metadata,
            "patterns": [],
            "registered_at": datetime.now().isoformat()
        }
        
        self.save_registry()
    
    def add_pattern_to_skill(self, skill_id: str, pattern: Pattern):
        """
        Add a pattern to a skill.
        
        Args:
            skill_id: Skill identifier
            pattern: Pattern to add
        """
        if skill_id not in self.skills:
            self.register_skill(skill_id, {"type": "unknown", "description": ""})
        
        self.skills[skill_id]["patterns"].append(pattern.id)
        self.patterns[pattern.id] = {
            "id": pattern.id,
            "source_skill": skill_id,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "success_count": pattern.success_count,
            "failure_count": pattern.failure_count,
            "last_used": pattern.last_used.isoformat(),
            "metadata": pattern.metadata
        }
        
        self.save_registry()
    
    def get_skill_patterns(self, skill_id: str) -> List[Pattern]:
        """
        Get all patterns for a skill.
        
        Args:
            skill_id: Skill identifier
        
        Returns:
            List of Patterns
        """
        patterns = []
        
        for pattern_id, pattern_data in self.patterns.items():
            if pattern_data["source_skill"] == skill_id:
                pattern = Pattern(
                    id=pattern_data["id"],
                    source_skill=pattern_data["source_skill"],
                    pattern_type=pattern_data["pattern_type"],
                    description=pattern_data["description"],
                    implementation=pattern_data.get("implementation"),
                    success_count=pattern_data["success_count"],
                    failure_count=pattern_data["failure_count"],
                    context=pattern_data.get("context", {}),
                    last_used=datetime.fromisoformat(pattern_data["last_used"]),
                    metadata=pattern_data.get("metadata", {})
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_all_patterns(self) -> List[Pattern]:
        """
        Get all patterns from all skills.
        
        Returns:
            List of Patterns
        """
        patterns = []
        
        for pattern_id, pattern_data in self.patterns.items():
            pattern = Pattern(
                id=pattern_data["id"],
                source_skill=pattern_data["source_skill"],
                pattern_type=pattern_data["pattern_type"],
                description=pattern_data["description"],
                implementation=pattern_data.get("implementation"),
                success_count=pattern_data["success_count"],
                failure_count=pattern_data["failure_count"],
                context=pattern_data.get("context", {}),
                last_used=datetime.fromisoformat(pattern_data["last_used"]),
                metadata=pattern_data.get("metadata", {})
            )
            patterns.append(pattern)
        
        return patterns
    
    def find_compatible_skills(self, skill_id: str) -> List[str]:
        """
        Find compatible skills for transfer.
        
        Args:
            skill_id: Skill identifier
        
        Returns:
            List of compatible skill IDs
        """
        compatible = []
        
        if skill_id not in self.compatibility_matrix:
            return compatible
        
        for other_skill_id, compatibility_score in self.compatibility_matrix[skill_id].items():
            if compatibility_score > 0.5:  # Medium or high compatibility
                compatible.append(other_skill_id)
        
        return compatible
    
    def record_transfer(self, transfer_result: TransferResult):
        """
        Record a pattern transfer result.
        
        Args:
            transfer_result: TransferResult to record
        """
        if transfer_result.pattern_id not in self.transfers:
            self.transfers[transfer_result.pattern_id] = []
        
        self.transfers[transfer_result.pattern_id].append({
            "source_skill": transfer_result.source_skill,
            "target_skill": transfer_result.target_skill,
            "success": transfer_result.success,
            "adapted": transfer_result.adapted,
            "adaptation_details": transfer_result.adaptation_details,
            "timestamp": transfer_result.timestamp.isoformat(),
            "feedback": transfer_result.feedback
        })
        
        # Update pattern success/failure count
        if transfer_result.pattern_id in self.patterns:
            if transfer_result.success:
                self.patterns[transfer_result.pattern_id]["success_count"] += 1
            else:
                self.patterns[transfer_result.pattern_id]["failure_count"] += 1
        
        self.save_registry()
    
    def track_transfer_success(self, pattern_id: str) -> Dict[str, Any]:
        """
        Track pattern transfer success metrics.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Transfer success metrics
        """
        transfers = self.transfers.get(pattern_id, [])
        
        if not transfers:
            return {"total": 0, "success": 0, "adapted": 0, "success_rate": 0.5}
        
        total = len(transfers)
        successful = sum(1 for t in transfers if t["success"])
        adapted = sum(1 for t in transfers if t["adapted"])
        
        return {
            "total": total,
            "success": successful,
            "adapted": adapted,
            "success_rate": successful / total if total > 0 else 0.5
        }


class PatternTransfer:
    """
    Transfer patterns between skills and domains.
    
    Transfer Types:
    - Direct transfer: Copy pattern as-is
    - Adapted transfer: Modify pattern for target skill
    - Inspired transfer: Use pattern as inspiration
    """
    
    def __init__(self, skill_registry: SkillRegistry = None,
                 transfer_evaluator: TransferEvaluator = None):
        self.skill_registry = skill_registry or SkillRegistry()
        self.transfer_evaluator = transfer_evaluator or TransferEvaluator()
    
    def transfer_pattern(self, pattern: Pattern, target_skill: str,
                         adaptation: str = "none") -> TransferResult:
        """
        Transfer a pattern to a target skill.
        
        Args:
            pattern: Pattern to transfer
            target_skill: Target skill name
            adaptation: Adaptation type ("none", "minimal", "extensive")
        
        Returns:
            TransferResult
        """
        timestamp = datetime.now()
        
        # Evaluate transfer suitability
        suitability = self.transfer_evaluator.evaluate_transfer(
            pattern, target_skill, pattern.source_skill
        )
        
        # Check if transfer is recommended
        if suitability.recommendation == "reject":
            return TransferResult(
                pattern_id=pattern.id,
                source_skill=pattern.source_skill,
                target_skill=target_skill,
                success=False,
                adapted=False,
                adaptation_details="Transfer rejected by evaluator",
                timestamp=timestamp,
                feedback=suitability.recommendation
            )
        
        # Perform transfer
        try:
            # Add pattern to target skill
            self.skill_registry.add_pattern_to_skill(target_skill, pattern)
            
            # Record transfer
            result = TransferResult(
                pattern_id=pattern.id,
                source_skill=pattern.source_skill,
                target_skill=target_skill,
                success=True,
                adapted=(adaptation != "none"),
                adaptation_details=adaptation,
                timestamp=timestamp,
                feedback="Transfer successful"
            )
            
            # Record transfer
            self.skill_registry.record_transfer(result)
            
            return result
            
        except Exception as e:
            # Transfer failed
            result = TransferResult(
                pattern_id=pattern.id,
                source_skill=pattern.source_skill,
                target_skill=target_skill,
                success=False,
                adapted=False,
                adaptation_details="",
                timestamp=timestamp,
                feedback=f"Transfer failed: {str(e)}"
            )
            
            # Record failed transfer
            self.skill_registry.record_transfer(result)
            
            return result
    
    def find_transferable_patterns(self, source_skill: str,
                                   target_skill: str) -> List[Tuple[Pattern, TransferSuitability]]:
        """
        Find transferable patterns between skills.
        
        Args:
            source_skill: Source skill name
            target_skill: Target skill name
        
        Returns:
            List of (Pattern, TransferSuitability) tuples
        """
        # Get patterns from source skill
        patterns = self.skill_registry.get_skill_patterns(source_skill)
        
        transferable = []
        
        for pattern in patterns:
            # Evaluate transfer suitability
            suitability = self.transfer_evaluator.evaluate_transfer(
                pattern, target_skill, source_skill
            )
            
            # Check if transfer is recommended
            if suitability.recommendation in ["transfer", "adapt"]:
                transferable.append((pattern, suitability))
        
        return transferable
    
    def perform_mass_transfer(self, source_skill: str,
                             target_skill: str,
                             max_transfers: int = 10) -> List[TransferResult]:
        """
        Perform mass pattern transfer between skills.
        
        Args:
            source_skill: Source skill name
            target_skill: Target skill name
            max_transfers: Maximum number of transfers
        
        Returns:
            List of TransferResults
        """
        # Find transferable patterns
        transferable = self.find_transferable_patterns(source_skill, target_skill)
        
        # Sort by transfer score (highest first)
        transferable.sort(key=lambda x: -x[1].transfer_score)
        
        # Perform transfers
        results = []
        transferred = 0
        
        for pattern, suitability in transferable:
            if transferred >= max_transfers:
                break
            
            # Perform transfer
            result = self.transfer_pattern(pattern, target_skill)
            results.append(result)
            
            transferred += 1
        
        return results
