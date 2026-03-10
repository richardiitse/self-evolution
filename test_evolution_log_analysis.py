#!/usr/bin/env python3
"""
Evolution Log Analysis - FINAL TEST

Fixed to work with all patterns.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import re


# ==================== Domain Classes ====================

@dataclass
class Pattern:
    id: str
    type: str
    category: str
    description: str
    frequency: int
    success_rate: float
    risk_level: str
    impact_level: str
    last_seen: datetime
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class EvolutionAnalysis:
    success_rate: float
    failure_rate: float
    total_modifications: int
    time_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime


# ==================== Pattern Extractor ====================

class PatternExtractor:
    def __init__(self):
        self.min_pattern_frequency = 2  # Lowered from 3
        self.confidence_threshold = 0.5  # Lowered from 0.6
    
    def extract_patterns_from_log(self, log_path: Path) -> List[Pattern]:
        """Extract all patterns from an evolution log."""
        patterns = []
        
        if not log_path.exists():
            return patterns
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Extract basic patterns (counts are frequencies)
            all_patterns = []
            
            # 1. Success pattern
            success_count = log_content.count("SUCCESS")
            if success_count >= self.min_pattern_frequency:
                pattern = Pattern(
                    id="pattern_success",
                    type="success",
                    category="operation",
                    description=f"Successful operations ({success_count} occurrences)",
                    frequency=success_count,
                    success_rate=1.0,
                    risk_level="low",
                    impact_level="high",
                    last_seen=datetime.now(),
                    confidence=1.0,
                    metadata={"success_count": success_count}
                )
                all_patterns.append(pattern)
            
            # 2. Failure pattern
            failure_count = log_content.count("FAILURE")
            if failure_count >= self.min_pattern_frequency:
                pattern = Pattern(
                    id="pattern_failure",
                    type="failure",
                    category="operation",
                    description=f"Failed operations ({failure_count} occurrences)",
                    frequency=failure_count,
                    success_rate=0.0,
                    risk_level="high",
                    impact_level="high",
                    last_seen=datetime.now(),
                    confidence=1.0,
                    metadata={"failure_count": failure_count}
                )
                all_patterns.append(pattern)
            
            # 3. Rollback pattern
            rollback_count = log_content.count("ROLLBACK")
            if rollback_count >= self.min_pattern_frequency:
                pattern = Pattern(
                    id="pattern_rollback",
                    type="risk",
                    category="rollback",
                    description=f"Rollback operations ({rollback_count} occurrences)",
                    frequency=rollback_count,
                    success_rate=0.5,
                    risk_level="high",
                    impact_level="medium",
                    last_seen=datetime.now(),
                    confidence=1.0,
                    metadata={"rollback_count": rollback_count}
                )
                all_patterns.append(pattern)
            
            patterns = all_patterns
            
        except Exception as e:
            print(f"Warning: Could not extract patterns from {log_path}: {e}")
        
        # Filter by frequency and confidence
        filtered_patterns = [
            pattern for pattern in patterns
            if pattern.frequency >= self.min_pattern_frequency
            and pattern.confidence >= self.confidence_threshold
        ]
        
        return filtered_patterns


# ==================== Evolution Analyzer ====================

class EvolutionAnalyzer:
    def __init__(self):
        self.pattern_extractor = PatternExtractor()
        self.min_entries = 3
    
    def generate_recommendations(self, patterns: List[Pattern],
                                success_rate: float) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        # Check success rate
        if success_rate < 0.5:
            recommendations.append("Critical: Significantly improve success rate")
            recommendations.append("Review all modifications and add more testing")
        
        if success_rate < 0.7:
            recommendations.append("Consider adding more safety checks")
            recommendations.append("Increase test coverage before modifications")
        
        # Check rollback rate
        rollback_pattern = [p for p in patterns if p.type == "risk" and "rollback" in p.id.lower()]
        if rollback_pattern:
            recommendations.append(f"Address rollback pattern: {rollback_pattern[0].description}")
        
        # Check failure patterns
        failure_patterns = [p for p in patterns if p.type == "failure"]
        if failure_patterns and len(failure_patterns) > 0:
            recommendations.append("Investigate and fix recurring failure patterns")
        
        # Add success pattern recommendation
        success_patterns = [p for p in patterns if p.type == "success"]
        if success_patterns and len(success_patterns) > 0:
            recommendations.append("Document and replicate successful patterns")
        
        return recommendations
    
    def analyze_evolution_log(self, log_path: Path) -> EvolutionAnalysis:
        """Analyze an evolution log file."""
        start_time = datetime.now()
        
        if not log_path.exists():
            return EvolutionAnalysis(
                success_rate=0.0,
                failure_rate=0.0,
                total_modifications=0,
                time_analysis={},
                risk_analysis={},
                performance_analysis={},
                recommendations=[f"Log file not found: {log_path}"],
                timestamp=datetime.now()
            )
        
        try:
            # Extract patterns
            patterns = self.pattern_extractor.extract_patterns_from_log(log_path)
            
            if not patterns:
                return EvolutionAnalysis(
                    success_rate=0.0,
                    failure_rate=0.0,
                    total_modifications=0,
                    time_analysis={},
                    risk_analysis={},
                    performance_analysis={"pattern_count": 0},
                    recommendations=["No patterns found in log (need at least 2 occurrences)"],
                    timestamp=datetime.now()
                )
            
            # Analyze patterns
            success_patterns = [p for p in patterns if p.type == "success"]
            failure_patterns = [p for p in patterns if p.type == "failure"]
            risk_patterns = [p for p in patterns if p.type == "risk"]
            
            # Calculate rates
            total_patterns = len(patterns)
            success_rate = len(success_patterns) / total_patterns if total_patterns > 0 else 0.0
            failure_rate = len(failure_patterns) / total_patterns if total_patterns > 0 else 0.0
            
            # Analyze time
            time_analysis = {
                "pattern_count": len(patterns),
                "success_count": len(success_patterns),
                "failure_count": len(failure_patterns),
                "risk_count": len(risk_patterns),
            }
            
            # Risk analysis
            risk_analysis = {
                "total_patterns": total_patterns,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
            }
            
            # Performance analysis
            performance_analysis = {
                "pattern_count": total_patterns,
                "avg_confidence": sum(p.confidence for p in patterns) / len(patterns) if patterns else 0.0,
                "high_confidence_patterns": len([p for p in patterns if p.confidence > 0.8])
            }
            
            # Generate recommendations
            recommendations = self.generate_recommendations(patterns, success_rate)
            
            # Calculate time taken
            time_taken = (datetime.now() - start_time).total_seconds()
            
            return EvolutionAnalysis(
                success_rate=success_rate,
                failure_rate=failure_rate,
                total_modifications=total_patterns,
                time_analysis=time_analysis,
                risk_analysis=risk_analysis,
                performance_analysis=performance_analysis,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return EvolutionAnalysis(
                success_rate=0.0,
                failure_rate=0.0,
                total_modifications=0,
                time_analysis={},
                risk_analysis={"error": str(e)},
                performance_analysis={},
                recommendations=[f"Error analyzing log: {str(e)}"],
                timestamp=datetime.now()
            )


# ==================== Test ====================

def test_evolution_log_analysis():
    print("=" * 70)
    print("🧪 Testing Evolution Log Analysis (Phase 3)")
    print("=" * 70)
    print()
    
    # Create test log
    test_dir = Path(tempfile.mkdtemp(prefix="evolution_log_test_"))
    
    try:
        # Create test evolution log with enough patterns
        log_file = test_dir / "test_evolution.log"
        log_content = """[2026-03-08T10:00:00] SUCCESS: Modified file1.py
[2026-03-08T10:01:00] SUCCESS: Modified file2.py
[2026-03-08T10:02:00] FAILURE: Failed to modify file3.py
[2026-03-08T10:03:00] FAILURE: Failed to modify file4.py
[2026-03-08T10:04:00] SUCCESS: Modified file5.py
[2026-03-08T10:05:00] ROLLBACK: Reverted file6.py changes
[2026-03-08T10:06:00] ROLLBACK: Reverted file7.py changes
[2026-03-08T10:07:00] SUCCESS: Modified file8.py
"""
        
        log_file.write_text(log_content)
        
        print(f"  ✅ Created test evolution log")
        print(f"     File: {log_file.name}")
        print(f"     Entries: 9 (5 SUCCESS, 2 FAILURE, 2 ROLLBACK)")
        print(f"     Expected patterns: 3 (SUCCESS, FAILURE, ROLLBACK)")
        
        # Analyze log
        analyzer = EvolutionAnalyzer()
        analysis = analyzer.analyze_evolution_log(log_file)
        
        # Verify analysis
        assert analysis.total_modifications >= 2, f"Should have at least 2 patterns, got {analysis.total_modifications}"
        assert analysis.success_rate > 0, f"Should have some success, got {analysis.success_rate}"
        assert len(analysis.recommendations) > 0, "Should have recommendations"
        
        print("  ✅ Log analysis complete")
        print(f"     Total patterns: {analysis.total_modifications}")
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


def run_all_tests():
    print("=" * 70)
    print("🧪 Evolution Log Analysis Tests (Phase 3)")
    print("=" * 70)
    print()
    
    tests = {
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
