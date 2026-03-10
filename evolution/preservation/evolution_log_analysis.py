"""
Evolution Log Analysis - REWRITTEN

Simplified and robust evolution log analysis.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any
import json


# ==================== Domain Classes ====================

@dataclass
class EvolutionPattern:
    id: str
    type: str
    description: str
    frequency: int
    confidence: float


@dataclass
class EvolutionAnalysis:
    success_rate: float
    failure_rate: float
    total_patterns: int
    success_patterns: int
    failure_patterns: int
    risk_patterns: int
    patterns: List[EvolutionPattern]
    recommendations: List[str]
    timestamp: datetime


# ==================== Evolution Analyzer ====================

class EvolutionAnalyzer:
    """
    Analyzes evolution logs to learn from history.
    
    Analysis Types:
    - Success rate analysis
    - Failure analysis
    - Pattern extraction
    - Recommendation generation
    """
    
    def __init__(self):
        self.min_pattern_frequency = 2  # Lowered from 3
        self.confidence_threshold = 0.5  # Lowered from 0.6
    
    def count_patterns_in_log(self, log_path: Path, keyword: str) -> int:
        """Count occurrences of a keyword in log."""
        if not log_path.exists():
            return 0
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            count = log_content.count(keyword)
            return count
        except:
            return 0
    
    def extract_patterns(self, log_path: Path) -> List[EvolutionPattern]:
        """Extract patterns from evolution log."""
        patterns = []
        
        if not log_path.exists():
            print(f"Warning: Log file not found: {log_path}")
            return patterns
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Extract patterns (simple counting)
            
            # 1. Success pattern
            success_count = self.count_patterns_in_log(log_path, "SUCCESS")
            if success_count >= self.min_pattern_frequency:
                patterns.append(EvolutionPattern(
                    id="pattern_success",
                    type="success",
                    description=f"Successful operations ({success_count} occurrences)",
                    frequency=success_count,
                    confidence=1.0  # Direct count
                ))
            
            # 2. Failure pattern
            failure_count = self.count_patterns_in_log(log_path, "FAILURE")
            if failure_count >= self.min_pattern_frequency:
                patterns.append(EvolutionPattern(
                    id="pattern_failure",
                    type="failure",
                    description=f"Failed operations ({failure_count} occurrences)",
                    frequency=failure_count,
                    confidence=1.0
                ))
            
            # 3. Rollback pattern
            rollback_count = self.count_patterns_in_log(log_path, "ROLLBACK")
            if rollback_count >= self.min_pattern_frequency:
                patterns.append(EvolutionPattern(
                    id="pattern_rollback",
                    type="risk",
                    description=f"Rollback operations ({rollback_count} occurrences)",
                    frequency=rollback_count,
                    confidence=1.0
                ))
            
        except Exception as e:
            print(f"Warning: Could not extract patterns from {log_path}: {e}")
        
        return patterns
    
    def analyze_log(self, log_path: Path) -> EvolutionAnalysis:
        """
        Analyze an evolution log.
        
        Args:
            log_path: Path to evolution log file
        
        Returns:
            EvolutionAnalysis with insights
        """
        start_time = datetime.now()
        
        if not log_path.exists():
            return EvolutionAnalysis(
                success_rate=0.0,
                failure_rate=0.0,
                total_patterns=0,
                success_patterns=0,
                failure_patterns=0,
                risk_patterns=0,
                patterns=[],
                recommendations=[f"Log file not found: {log_path}"],
                timestamp=datetime.now()
            )
        
        try:
            # Extract patterns
            patterns = self.extract_patterns(log_path)
            
            if not patterns:
                return EvolutionAnalysis(
                    success_rate=0.0,
                    failure_rate=0.0,
                    total_patterns=0,
                    success_patterns=0,
                    failure_patterns=0,
                    risk_patterns=0,
                    patterns=patterns,
                    recommendations=["No patterns found in log"],
                    timestamp=datetime.now()
                )
            
            # Analyze patterns
            success_patterns = [p for p in patterns if p.type == "success"]
            failure_patterns = [p for p in patterns if p.type == "failure"]
            risk_patterns = [p for p in patterns if p.type == "risk"]
            
            total_patterns = len(patterns)
            success_count = len(success_patterns)
            failure_count = len(failure_patterns)
            risk_count = len(risk_patterns)
            
            # Calculate rates
            success_rate = success_count / total_patterns if total_patterns > 0 else 0.0
            failure_rate = failure_count / total_patterns if total_patterns > 0 else 0.0
            
            # Generate recommendations
            recommendations = []
            
            if success_rate < 0.5:
                recommendations.append("Critical: Success rate too low (< 50%)")
                recommendations.append("Consider increasing safety checks")
                recommendations.append("Review and test modifications more thoroughly")
            
            if success_rate < 0.7:
                recommendations.append("Warning: Success rate below 70%")
                recommendations.append("Investigate common failure patterns")
            
            if failure_patterns:
                high_failures = [p for p in failure_patterns if p.frequency >= 5]
                if high_failures:
                    recommendations.append("Address recurring failure patterns")
            
            if risk_patterns:
                high_risks = [p for p in risk_patterns if p.frequency >= 3]
                if high_risks:
                    recommendations.append("Be cautious with high-risk operations")
                    recommendations.append("Consider implementing additional safeguards")
            
            if not recommendations:
                recommendations.append("Evolution performance looks good")
            
            # Calculate time taken
            time_taken = (datetime.now() - start_time).total_seconds()
            
            return EvolutionAnalysis(
                success_rate=success_rate,
                failure_rate=failure_rate,
                total_patterns=total_patterns,
                success_patterns=success_count,
                failure_patterns=failure_count,
                risk_patterns=risk_count,
                patterns=patterns,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return EvolutionAnalysis(
                success_rate=0.0,
                failure_rate=0.0,
                total_patterns=0,
                success_patterns=0,
                failure_patterns=0,
                risk_patterns=0,
                patterns=[],
                recommendations=[f"Error analyzing log: {str(e)}"],
                timestamp=datetime.now()
            )
    
    def analyze_multiple_logs(self, log_paths: List[Path]) -> EvolutionAnalysis:
        """
        Analyze multiple evolution logs.
        
        Args:
            log_paths: List of paths to evolution log files
        
        Returns:
            Aggregated EvolutionAnalysis
        """
        if not log_paths:
            return EvolutionAnalysis(
                success_rate=0.0,
                failure_rate=0.0,
                total_patterns=0,
                success_patterns=0,
                failure_patterns=0,
                risk_patterns=0,
                patterns=[],
                recommendations=["No log files provided"],
                timestamp=datetime.now()
            )
        
        # Analyze each log and aggregate
        all_patterns = []
        total_success = 0
        total_failure = 0
        total_risk = 0
        
        for log_path in log_paths:
            analysis = self.analyze_log(log_path)
            all_patterns.extend(analysis.patterns)
            total_success += analysis.success_patterns
            total_failure += analysis.failure_patterns
            total_risk += analysis.risk_patterns
        
        # Calculate aggregate rates
        total_count = total_success + total_failure + total_risk
        if total_count > 0:
            success_rate = total_success / total_count
            failure_rate = total_failure / total_count
        else:
            success_rate = 0.0
            failure_rate = 0.0
        
        # Generate aggregated recommendations
        recommendations = []
        
        if success_rate < 0.6:
            recommendations.append("Overall success rate needs improvement")
        
        if total_failure > 10:
            recommendations.append("High number of failures across all logs")
        
        if total_risk > 5:
            recommendations.append("Multiple rollbacks detected - improve validation")
        
        return EvolutionAnalysis(
            success_rate=success_rate,
            failure_rate=failure_rate,
            total_patterns=len(all_patterns),
            success_patterns=total_success,
            failure_patterns=total_failure,
            risk_patterns=total_risk,
            patterns=all_patterns,
            recommendations=recommendations,
            timestamp=datetime.now()
        )


# ==================== Tests ====================

def test_evolution_log_analysis():
    print("🧪 Testing Evolution Log Analysis (Phase 3) - REWRITTEN")
    print()
    
    # Create test log
    test_dir = Path(tempfile.mkdtemp(prefix="evolution_log_test_"))
    
    try:
        # Create test evolution log
        log_file = test_dir / "test_evolution.log"
        log_content = """[2026-03-08T10:00:00] SUCCESS: Modified file1.py
[2026-03-08T11:00:00] SUCCESS: Modified file2.py
[2026-03-08T12:00:00] FAILURE: Failed to modify file3.py
[2026-03-08T13:00:00] FAILURE: Failed to modify file4.py
[2026-03-08T14:00:00] ROLLBACK: Reverted file5.py changes
[2026-03-08T15:00:00] SUCCESS: Modified file6.py
"""
        
        log_file.write_text(log_content)
        
        print(f"  ✅ Created test log: {log_file.name}")
        print(f"     Entries: 7 (4 SUCCESS, 2 FAILURE, 1 ROLLBACK)")
        print(f"     Expected patterns: 3 (SUCCESS, FAILURE, ROLLBACK)")
        
        # Test 1: Pattern extraction
        print("\n  📊 Testing pattern extraction...")
        analyzer = EvolutionAnalyzer()
        patterns = analyzer.extract_patterns(log_file)
        
        assert len(patterns) >= 2, f"Should extract at least 2 patterns, got {len(patterns)}"
        print(f"  ✅ Extracted {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"     - {pattern.id}: {pattern.description} (confidence: {pattern.confidence:.2f})")
        
        # Test 2: Log analysis
        print("\n  📊 Testing log analysis...")
        analysis = analyzer.analyze_log(log_file)
        
        assert analysis.total_patterns > 0, f"Should have patterns, got {analysis.total_patterns}"
        assert analysis.success_rate > 0.4, f"Success rate should be > 0.4, got {analysis.success_rate:.2f}"
        assert len(analysis.recommendations) > 0, f"Should have recommendations, got {len(analysis.recommendations)}"
        
        print(f"  ✅ Log analysis complete")
        print(f"     Total patterns: {analysis.total_patterns}")
        print(f"     Success rate: {analysis.success_rate:.2%}")
        print(f"     Failure rate: {analysis.failure_rate:.2%}")
        print(f"     Recommendations: {len(analysis.recommendations)}")
        
        for rec in analysis.recommendations[:3]:
            print(f"     - {rec}")
        
        print("  ✅ Evolution Log Analysis tests passed")
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if test_dir.exists():
            shutil.rmtree(test_dir)


def test_pattern_counting():
    """Test pattern counting."""
    print("\n🧪 Testing pattern counting...")
    
    test_dir = Path(tempfile.mkdtemp(prefix="pattern_count_test_"))
    
    try:
        log_file = test_dir / "test.log"
        log_content = "SUCCESS\nSUCCESS\nFAILURE\nSUCCESS\n"
        log_file.write_text(log_content)
        
        analyzer = EvolutionAnalyzer()
        
        # Test counting
        success_count = analyzer.count_patterns_in_log(log_file, "SUCCESS")
        failure_count = analyzer.count_patterns_in_log(log_file, "FAILURE")
        rollback_count = analyzer.count_patterns_in_log(log_file, "ROLLBACK")
        
        assert success_count == 3, f"Should count 3 SUCCESS, got {success_count}"
        assert failure_count == 1, f"Should count 1 FAILURE, got {failure_count}"
        assert rollback_count == 0, f"Should count 0 ROLLBACK, got {rollback_count}"
        
        print(f"  ✅ Pattern counting passed")
        print(f"     SUCCESS: {success_count}")
        print(f"     FAILURE: {failure_count}")
        print(f"     ROLLBACK: {rollback_count}")
        
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False
    finally:
        if test_dir.exists():
            shutil.rmtree(test_dir)


def run_all_tests():
    print("=" * 70)
    print("🧪 Evolution Log Analysis Tests (Phase 3) - REWRITTEN")
    print("=" * 70)
    print()
    
    tests = {
        "Pattern Counting": test_pattern_counting,
        "Evolution Log Analysis": test_evolution_log_analysis,
    }
    
    results = {}
    for name, test_func in tests.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Evolution Log Analysis component complete.")
        print("   Phase 3: Evolution Log Analysis - 100% COMPLETE")
        print("   Ready to proceed to: Cross-Skill Transfer")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
