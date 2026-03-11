"""
Safe Self-Modification Protocol.

Based on MIRI corrigibility research: implements safe code modification with
robust validation, rollback capabilities, and safety constraints.
"""

import ast
import os
import shutil
import copy
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from enum import Enum


class ModificationType(Enum):
    """Types of code modifications."""
    FUNCTION_CHANGE = "function_change"
    CLASS_CHANGE = "class_change"
    IMPORT_CHANGE = "import_change"
    CONFIG_CHANGE = "config_change"
    REFACTORING = "refactoring"
    BUGFIX = "bugfix"
    FEATURE_ADDITION = "feature_addition"
    SAFETY_PATCH = "safety_patch"


class SafetyConstraint(Enum):
    """MIRI safety constraints for self-modification."""
    MAINTAIN_CORRIGIBILITY = "maintain_corrigibility"
    PRESERVE_ROLLBACK = "preserve_rollback"
    NO_OBJECTIVE_DRIFT = "no_objective_drift"
    TRANSPARENT_LOGGING = "transparent_logging"
    HUMAN_OVERSIGHT = "human_oversight"
    GRADUAL_CHANGE = "gradual_change"
    TEST_VERIFICATION = "test_verification"


@dataclass
class ModificationPlan:
    """
    Plan for a code modification with full safety validation.

    Includes all necessary information for safe execution and rollback.
    """
    plan_id: str
    target_files: List[str]
    changes: List[Dict[str, Any]]
    validation_rules: List[str]
    rollback_plan: Dict[str, Any]
    safety_constraints: List[SafetyConstraint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    estimated_impact: str = "unknown"  # low, medium, high

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for serialization."""
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        result['safety_constraints'] = [c.value for c in self.safety_constraints]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModificationPlan':
        """Create plan from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'safety_constraints' in data:
            data['safety_constraints'] = [SafetyConstraint(c) for c in data['safety_constraints']]
        return cls(**data)


@dataclass
class ModificationResult:
    """Result of a modification operation."""
    success: bool
    target: str
    change_type: str
    modifications_made: List[str]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    backup_path: Optional[str] = None
    checksum_before: Optional[str] = None
    checksum_after: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    confidence: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    safety_constraints_met: List[str] = field(default_factory=list)
    safety_constraints_violated: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApplicationResult:
    """Result of applying a modification plan."""
    success: bool
    plan_id: str
    files_modified: List[str]
    total_changes: int
    rollback_available: bool
    rollback_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class CodeModifier:
    """
    Safely modifies code with full validation and rollback support.

    Implements MIRI's corrigibility principles: all changes must be
    reversible, validated, and logged.
    """

    def __init__(self, backup_dir: Optional[str] = None):
        """
        Initialize code modifier.

        Args:
            backup_dir: Directory for backups (default: .evolution/backups/)
        """
        if backup_dir is None:
            backup_dir = os.path.join(os.getcwd(), '.evolution', 'backups')

        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.modification_history: List[ModificationResult] = []

    def apply_change(self,
                    target: str,
                    change: Dict[str, Any],
                    create_backup: bool = True) -> ModificationResult:
        """
        Apply a single change to a target file.

        Args:
            target: Path to target file
            change: Change specification (type, content, location, etc.)
            create_backup: Whether to create backup before modification

        Returns:
            ModificationResult with outcome details
        """
        result = ModificationResult(
            success=False,
            target=target,
            change_type=change.get('type', 'unknown'),
            modifications_made=[]
        )

        try:
            target_path = Path(target)
            if not target_path.exists():
                result.errors.append(f"Target file not found: {target}")
                return result

            # Create backup if requested
            if create_backup:
                backup_path = self._create_backup(target_path)
                result.backup_path = str(backup_path)
                result.checksum_before = self._calculate_checksum(target_path)

            # Read current content
            with open(target_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Apply change based on type
            modified_content = self._apply_change_to_content(original_content, change)

            # Validate syntax
            if not self.validate_syntax(modified_content):
                result.errors.append("Syntax validation failed after modification")
                return result

            # Write modified content
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            result.checksum_after = self._calculate_checksum(target_path)
            result.modifications_made.append(change.get('description', 'Change applied'))
            result.success = True

            self.modification_history.append(result)

        except Exception as e:
            result.errors.append(f"Exception during modification: {str(e)}")

        return result

    def _apply_change_to_content(self, content: str, change: Dict[str, Any]) -> str:
        """Apply change to file content."""
        change_type = change.get('type', '')

        if change_type == 'replace_text':
            old_text = change['old']
            new_text = change['new']
            return content.replace(old_text, new_text)

        elif change_type == 'insert_text':
            position = change.get('position', 'end')
            text = change['text']

            if position == 'start':
                return text + '\n' + content
            elif position == 'end':
                return content + '\n' + text
            else:
                # Line-based insertion
                lines = content.split('\n')
                line_num = change.get('line_number', len(lines))
                lines.insert(line_num, text)
                return '\n'.join(lines)

        elif change_type == 'delete_text':
            text_to_remove = change['text']
            return content.replace(text_to_remove, '')

        elif change_type == 'replace_function':
            old_function = change['old_function']
            new_function = change['new_function']
            return content.replace(old_function, new_function)

        else:
            raise ValueError(f"Unknown change type: {change_type}")

    def validate_syntax(self, code: str) -> bool:
        """
        Validate Python syntax.

        Args:
            code: Code to validate

        Returns:
            True if syntax is valid
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _create_backup(self, target_path: Path) -> Path:
        """Create backup of target file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{target_path.stem}_{timestamp}.backup{target_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(target_path, backup_path)
        return backup_path

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def restore_from_backup(self, target: str, backup_path: str) -> bool:
        """
        Restore file from backup.

        Args:
            target: Path to target file
            backup_path: Path to backup file

        Returns:
            True if restoration successful
        """
        try:
            target_path = Path(target)
            backup = Path(backup_path)

            if not backup.exists():
                return False

            shutil.copy2(backup, target_path)
            return True
        except Exception:
            return False


class ChangeValidator:
    """
    Validates proposed changes against safety constraints.

    Implements MIRI corrigibility: changes must preserve safety properties,
    maintain transparency, and support rollback.
    """

    def __init__(self):
        """Initialize change validator."""
        self.validation_rules: Dict[str, Callable] = {
            'syntax': self._validate_syntax,
            'safety': self._validate_safety_constraints,
            'corrigibility': self._validate_corrigibility,
            'rollback': self._validate_rollback_capability,
            'transparency': self._validate_transparency,
            'gradual': self._validate_gradual_change,
        }

    def validate_change(self, change: Dict[str, Any]) -> ValidationResult:
        """
        Validate a proposed change.

        Args:
            change: Change specification

        Returns:
            ValidationResult with detailed findings
        """
        result = ValidationResult(
            is_valid=True,
            confidence=0.0,
            safety_constraints_met=[],
            safety_constraints_violated=[]
        )

        # Run all validation rules
        passed_validations = 0
        total_validations = len(self.validation_rules)

        for rule_name, rule_func in self.validation_rules.items():
            try:
                rule_result = rule_func(change)
                if rule_result['passed']:
                    passed_validations += 1
                    if 'constraint' in rule_result:
                        result.safety_constraints_met.append(rule_result['constraint'])
                else:
                    result.is_valid = False
                    if 'constraint' in rule_result:
                        result.safety_constraints_violated.append(rule_result['constraint'])
                    result.errors.extend(rule_result.get('errors', []))
                    result.warnings.extend(rule_result.get('warnings', []))
            except Exception as e:
                result.warnings.append(f"Validation rule '{rule_name}' failed: {str(e)}")

        result.confidence = passed_validations / total_validations if total_validations > 0 else 0.0

        # Overall validity depends on critical rules
        critical_rules = ['syntax', 'safety']
        for rule in critical_rules:
            if rule in result.safety_constraints_violated:
                result.is_valid = False

        return result

    def check_safety_constraints(self, change: Dict[str, Any]) -> bool:
        """
        Check if change satisfies safety constraints.

        Args:
            change: Change specification

        Returns:
            True if all safety constraints satisfied
        """
        result = self._validate_safety_constraints(change)
        return result['passed']

    def check_corrigibility(self, change: Dict[str, Any]) -> bool:
        """
        Check if change maintains corrigibility.

        Args:
            change: Change specification

        Returns:
            True if corrigibility preserved
        """
        result = self._validate_corrigibility(change)
        return result['passed']

    def _validate_syntax(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Python syntax of change."""
        if 'code' not in change:
            return {'passed': True}  # Not applicable

        try:
            ast.parse(change['code'])
            return {
                'passed': True,
                'constraint': SafetyConstraint.TEST_VERIFICATION.value
            }
        except SyntaxError as e:
            return {
                'passed': False,
                'constraint': SafetyConstraint.TEST_VERIFICATION.value,
                'errors': [f"Syntax error: {str(e)}"]
            }

    def _validate_safety_constraints(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MIRI safety constraints."""
        errors = []

        # Check for dangerous patterns
        dangerous_patterns = [
            'eval(',
            'exec(',
            'compile(',
            '__import__',
            'globals()',
            'locals()',
        ]

        code = change.get('code', '')
        for pattern in dangerous_patterns:
            if pattern in code:
                errors.append(f"Dangerous pattern detected: {pattern}")

        return {
            'passed': len(errors) == 0,
            'constraint': SafetyConstraint.MAINTAIN_CORRIGIBILITY.value,
            'errors': errors
        }

    def _validate_corrigibility(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that change preserves corrigibility."""
        # Check for anti-corrigibility patterns
        warnings = []

        code = change.get('code', '')

        # Check for modifications to shutdown/disable mechanisms
        if 'def shutdown' in code.lower() and 'disabled' in code.lower():
            warnings.append("Potential modification to shutdown mechanism")

        # Check for removal of safety checks
        if 'safety_check' in code.lower() and 'return True' in code:
            warnings.append("Potential bypass of safety checks")

        return {
            'passed': len(warnings) == 0,
            'constraint': SafetyConstraint.MAINTAIN_CORRIGIBILITY.value,
            'warnings': warnings
        }

    def _validate_rollback_capability(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that change can be rolled back."""
        # Check if change includes rollback information
        if 'rollback_info' not in change:
            return {
                'passed': False,
                'constraint': SafetyConstraint.PRESERVE_ROLLBACK.value,
                'warnings': ['No rollback information provided']
            }

        return {
            'passed': True,
            'constraint': SafetyConstraint.PRESERVE_ROLLBACK.value
        }

    def _validate_transparency(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that change maintains transparency."""
        # Check for logging/documentation
        code = change.get('code', '')

        has_logging = 'log' in code.lower() or 'print' in code.lower()
        has_docstring = '"""' in code or "'''" in code

        if has_logging or has_docstring:
            return {
                'passed': True,
                'constraint': SafetyConstraint.TRANSPARENT_LOGGING.value
            }

        return {
            'passed': False,
            'constraint': SafetyConstraint.TRANSPARENT_LOGGING.value,
            'warnings': ['Change lacks sufficient logging or documentation']
        }

    def _validate_gradual_change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that change is gradual (not too large)."""
        code = change.get('code', '')
        lines = code.split('\n')

        # Gradual change heuristic: max 100 lines per change
        if len(lines) > 100:
            return {
                'passed': False,
                'constraint': SafetyConstraint.GRADUAL_CHANGE.value,
                'warnings': [f'Change too large ({len(lines)} lines), consider breaking into smaller changes']
            }

        return {
            'passed': True,
            'constraint': SafetyConstraint.GRADUAL_CHANGE.value
        }


class ChangeApplicator:
    """
    Applies validated changes with full rollback support.

    Implements MIRI principle: all modifications must be reversible
    and applied atomically where possible.
    """

    def __init__(self, code_modifier: Optional[CodeModifier] = None):
        """
        Initialize change applicator.

        Args:
            code_modifier: CodeModifier instance to use
        """
        self.code_modifier = code_modifier or CodeModifier()
        self.validator = ChangeValidator()
        self.applied_plans: Dict[str, ApplicationResult] = {}

    def apply_modification(self, plan: ModificationPlan) -> ApplicationResult:
        """
        Apply a complete modification plan.

        Args:
            plan: ModificationPlan to execute

        Returns:
            ApplicationResult with execution details
        """
        result = ApplicationResult(
            success=False,
            plan_id=plan.plan_id,
            files_modified=[],
            total_changes=0,
            rollback_available=False
        )

        try:
            # Validate all changes first
            for change in plan.changes:
                validation = self.validator.validate_change(change)
                if not validation.is_valid:
                    result.errors.extend(
                        f"Validation failed for change: {e}"
                        for e in validation.errors
                    )
                    return result

            # Create plan-level backup directory
            plan_backup_dir = self.code_modifier.backup_dir / plan.plan_id
            plan_backup_dir.mkdir(exist_ok=True)
            result.rollback_path = str(plan_backup_dir)

            # Apply each change
            for change in plan.changes:
                target = change.get('target', '')
                if target not in result.files_modified:
                    result.files_modified.append(target)

                mod_result = self.code_modifier.apply_change(
                    target,
                    change,
                    create_backup=True
                )

                if not mod_result.success:
                    result.errors.extend(mod_result.errors)
                    # Rollback all changes
                    self._rollback_plan(result)
                    return result

                result.warnings.extend(mod_result.warnings)
                result.total_changes += 1

            result.success = True
            result.rollback_available = True

            # Store result
            self.applied_plans[plan.plan_id] = result

        except Exception as e:
            result.errors.append(f"Exception during application: {str(e)}")
            self._rollback_plan(result)

        return result

    def apply_with_rollback(self, change: Dict[str, Any]) -> ApplicationResult:
        """
        Apply a single change with automatic rollback on failure.

        Args:
            change: Change specification

        Returns:
            ApplicationResult with execution details
        """
        plan = ModificationPlan(
            plan_id=f"single_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            target_files=[change.get('target', '')],
            changes=[change],
            validation_rules=['syntax', 'safety', 'corrigibility'],
            rollback_plan={'enabled': True}
        )

        return self.apply_modification(plan)

    def rollback_plan(self, plan_id: str) -> bool:
        """
        Rollback a previously applied plan.

        Args:
            plan_id: ID of plan to rollback

        Returns:
            True if rollback successful
        """
        if plan_id not in self.applied_plans:
            return False

        result = self.applied_plans[plan_id]

        if not result.rollback_available:
            return False

        try:
            return self._rollback_plan(result)
        except Exception:
            return False

    def _rollback_plan(self, result: ApplicationResult) -> bool:
        """Internal rollback implementation."""
        if not result.rollback_path:
            return False

        try:
            backup_dir = Path(result.rollback_path)
            if not backup_dir.exists():
                return False

            # Restore from backups
            for backup_file in backup_dir.glob('*.backup*'):
                # Extract original filename
                original_name = backup_file.stem.split('_')[0]
                original_path = backup_file.parent.parent / f"{original_name}{backup_file.suffix.replace('.backup', '')}"

                if backup_file.exists():
                    shutil.copy2(backup_file, original_path)

            return True
        except Exception:
            return False

    def get_applied_plans(self) -> List[str]:
        """Get list of successfully applied plan IDs."""
        return [
            plan_id for plan_id, result in self.applied_plans.items()
            if result.success
        ]
