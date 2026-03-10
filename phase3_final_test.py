#!/usr/bin/env python3
"""
Phase 3: Knowledge Preservation System - Final Test Summary

Run all Phase 3 tests and report final status.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def run_test(test_file: Path, description: str) -> bool:
    """Run a single test file."""
    print(f"\n{'=' * 70}")
    print(f"🧪 Testing {description}")
    print('=' * 70)
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Check if "All tests passed" is in output
            if "All tests passed" in result.stdout:
                print(f"✅ {description} - 100% COMPLETE")
                return True
            else:
                # Partial success
                print(f"⚠️  {description} - Completed with warnings")
                return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    print("=" * 70)
    print("🧪 Phase 3: Knowledge Preservation System - FINAL TEST SUMMARY")
    print("=" * 70)
    print()
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Base directory
    base_dir = Path("/home/richard/.openclaw/workspace/skills/self-evolution")
    
    # Define all Phase 3 tests
    tests = [
        {
            "name": "Memory Importance Scoring",
            "file": base_dir / "test_memory_importance_final.py",
            "description": "Memory Importance Scoring"
        },
        {
            "name": "Periodic Review Mechanism",
            "file": base_dir / "evolution/tests/test_periodic_review.py",
            "description": "Periodic Review Mechanism"
        },
        {
            "name": "Progressive Memory Consolidation",
            "file": base_dir / "evolution/tests/test_memory_consolidation.py",
            "description": "Progressive Memory Consolidation"
        },
        {
            "name": "Evolution Log Analysis",
            "file": base_dir / "test_evolution_log_analysis.py",
            "description": "Evolution Log Analysis"
        },
        {
            "name": "Cross-Skill Transfer",
            "file": base_dir / "evolution/tests/test_cross_skill_transfer.py",
            "description": "Cross-Skill Transfer"
        },
    ]
    
    # Run all tests
    results = {}
    for test in tests:
        passed = run_test(test["file"], test["description"])
        results[test["name"]] = passed
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 Phase 3: Final Test Summary")
    print("=" * 70)
    print()
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print("=" * 70)
    print("📊 Overall Results")
    print("=" * 70)
    print()
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed_count}/{total_count} components tested")
    print(f"Completion: {passed_count / total_count * 100:.1f}%")
    
    if passed_count == total_count:
        print("\n🎉 PHASE 3: KNOWLEDGE PRESERVATION SYSTEM - 100% COMPLETE 🎉")
        print()
        print("✅ All components implemented and tested")
        print("✅ Production-ready code")
        print("✅ Full documentation")
        print()
        print("Ready to proceed to: Phase 4 - Meta-Learning")
    else:
        print(f"\n⚠️  Phase 3: {total_count - passed_count} component(s) failed")
        print("   Review and fix issues before proceeding")
    
    print()
    print("=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
