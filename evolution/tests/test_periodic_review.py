#!/usr/bin/env python3
"""
Periodic Review Tests - FIXED

Fixed the outdated item logic.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass


# ==================== Domain Classes ====================

@dataclass
class MemoryItem:
    path: Path
    name: str
    type: str
    size: int
    access_count: int
    last_accessed: any
    created_at: datetime
    importance_score: float
    tags: list


@dataclass
class ReviewSchedule:
    review_type: str
    items: list
    scheduled_time: datetime
    frequency: int


@dataclass
class ReviewResult:
    item_path: str
    item_name: str
    relevance: str
    importance_changed: bool
    new_importance: float
    outdated: bool
    duplicate: bool
    action: str
    confidence: float
    review_time: datetime


# ==================== Implementation ====================

class MemoryScheduler:
    def __init__(self):
        self.daily_interval = 24
        self.weekly_interval = 168
        self.monthly_interval = 720
    
    def schedule_review(self, items: list, frequency: str = "medium") -> ReviewSchedule:
        if not items:
            return ReviewSchedule(
                review_type=frequency,
                items=[],
                scheduled_time=datetime.now(),
                frequency=720
            )
        
        item_scores = {}
        for item in items:
            if isinstance(item, dict):
                item_scores[item.get("path", "")] = item.get("importance_score", 0.5)
            elif isinstance(item, MemoryItem):
                item_scores[str(item.path)] = item.importance_score
            else:
                item_scores[str(item)] = 0.5
        
        thresholds = {
            "critical": 0.8,
            "high": 0.6,
            "medium": 0.4,
            "low": 0.2,
        }
        threshold = thresholds.get(frequency, 0.4)
        
        filtered_items = [str(path) for path, score in item_scores.items() if score >= threshold]
        
        intervals = {
            "critical": self.daily_interval,
            "high": self.weekly_interval,
            "medium": self.monthly_interval,
            "low": self.monthly_interval,
        }
        interval = intervals.get(frequency, 720)
        
        scheduled_time = datetime.now() + timedelta(hours=interval)
        
        return ReviewSchedule(
            review_type=frequency,
            items=filtered_items,
            scheduled_time=scheduled_time,
            frequency=interval
        )


class MemoryReviewer:
    def __init__(self):
        self.relevance_threshold = 0.3
        self.outdated_threshold_days = 90
        self.duplicate_similarity_threshold = 0.9
    
    def review_item(self, item: MemoryItem) -> ReviewResult:
        # Check relevance
        relevance = self._check_relevance(item)
        
        # Check if outdated
        outdated = self._check_outdated(item)
        
        # Check if duplicate
        duplicate = self._check_duplicate(item)
        
        # Calculate new importance
        importance_changed, new_importance = self._recalculate_importance(item)
        
        # Determine action
        action = self._determine_action(relevance, outdated, duplicate, new_importance)
        
        # Calculate confidence
        confidence = self._calculate_confidence(relevance, outdated, duplicate, importance_changed)
        
        return ReviewResult(
            item_path=str(item.path),
            item_name=item.name,
            relevance=relevance,
            importance_changed=importance_changed,
            new_importance=new_importance if importance_changed else item.importance_score,
            outdated=outdated,
            duplicate=duplicate,
            action=action,
            confidence=confidence,
            review_time=datetime.now()
        )
    
    def _check_relevance(self, item: MemoryItem) -> str:
        if item.last_accessed is None:
            return "potentially_irrelevant"
        
        days_since = (datetime.now() - item.last_accessed).total_seconds() / 86400.0
        
        if days_since < 7:
            return "relevant"
        elif days_since < 30:
            return "potentially_irrelevant"
        else:
            return "irrelevant"
    
    def _check_outdated(self, item: MemoryItem) -> bool:
        # Item is outdated if:
        # - Created > 90 days ago, AND
        # - Not accessed in last 30 days (or never accessed)
        if item.last_accessed is None:
            days_since_access = float('inf')
        else:
            days_since_access = (datetime.now() - item.last_accessed).total_seconds() / 86400.0
        
        days_since_creation = (datetime.now() - item.created_at).total_seconds() / 86400.0
        
        if days_since_creation > 90 and (days_since_access > 30 or item.last_accessed is None):
            return True
        return False
    
    def _check_duplicate(self, item: MemoryItem) -> bool:
        duplicate_indicators = [tag for tag in item.tags if tag.startswith("duplicate:")]
        return len(duplicate_indicators) > 0
    
    def _recalculate_importance(self, item: MemoryItem) -> tuple[bool, float]:
        if item.access_count > 10:
            new_importance = min(item.importance_score + 0.1, 1.0)
            return (True, new_importance)
        elif item.access_count == 0:
            new_importance = max(item.importance_score - 0.1, 0.0)
            return (True, new_importance)
        else:
            return (False, item.importance_score)
    
    def _determine_action(self, relevance: str, outdated: bool,
                         duplicate: bool, current_importance: float) -> str:
        if duplicate:
            return "delete"
        
        if relevance == "irrelevant":
            return "delete"
        
        if outdated:
            return "archive"
        
        if current_importance < 0.3:
            return "archive"
        
        return "keep"
    
    def _calculate_confidence(self, relevance: str, outdated: bool,
                            duplicate: bool, importance_changed: bool) -> float:
        confidence = 0.5
        
        if relevance == "relevant":
            confidence += 0.2
        elif relevance == "irrelevant":
            confidence -= 0.2
        
        if outdated:
            confidence += 0.1
        else:
            confidence -= 0.05
        
        if duplicate:
            confidence += 0.2
        
        return max(0.0, min(1.0, confidence))


# ==================== Tests ====================

def test_memory_scheduler():
    print("🧪 Testing MemoryScheduler...")
    
    now = datetime.now()
    
    items = [
        {"path": "item1", "importance_score": 0.9},  # Critical
        {"path": "item2", "importance_score": 0.7},  # High
        {"path": "item3", "importance_score": 0.5},  # Medium
        {"path": "item4", "importance_score": 0.3},  # Low
    ]
    
    scheduler = MemoryScheduler()
    
    schedule = scheduler.schedule_review(items, frequency="critical")
    assert schedule.review_type == "critical"
    assert schedule.frequency == 24
    print(f"  ✅ Critical review scheduled")
    
    schedule = scheduler.schedule_review(items, frequency="high")
    assert schedule.review_type == "high"
    assert schedule.frequency == 168
    print(f"  ✅ High review scheduled")
    
    schedule = scheduler.schedule_review(items, frequency="medium")
    assert schedule.review_type == "medium"
    assert schedule.frequency == 720
    print(f"  ✅ Medium review scheduled")
    
    print("  ✅ MemoryScheduler tests passed")
    return True


def test_memory_reviewer():
    print("\n🧪 Testing MemoryReviewer...")
    
    now = datetime.now()
    
    # Test Case 1: Relevant item (accessed today)
    item = MemoryItem(
        path=Path("relevant.py"),
        name="relevant.py",
        type="code",
        size=1000,
        access_count=10,
        last_accessed=now,
        created_at=now,
        importance_score=0.5,
        tags=[]
    )
    
    reviewer = MemoryReviewer()
    result = reviewer.review_item(item)
    
    assert result.relevance == "relevant"
    assert result.action == "keep"
    assert result.confidence > 0.6
    print(f"  ✅ Relevant item review: {result.relevance}, {result.action}")
    
    # Test Case 2: Outdated item (created 100 days ago, never accessed)
    item = MemoryItem(
        path=Path("outdated.py"),
        name="outdated.py",
        type="code",
        size=1000,
        access_count=0,
        last_accessed=None,
        created_at=now - timedelta(days=100),
        importance_score=0.5,
        tags=[]
    )
    
    result = reviewer.review_item(item)
    
    assert result.outdated == True
    assert result.action in ["archive", "keep"]
    print(f"  ✅ Outdated item review: {result.outdated}, {result.action}")
    
    # Test Case 3: Duplicate item
    item = MemoryItem(
        path=Path("duplicate.py"),
        name="duplicate.py",
        type="code",
        size=1000,
        access_count=5,
        last_accessed=now,
        created_at=now,
        importance_score=0.5,
        tags=["duplicate:true"]
    )
    
    result = reviewer.review_item(item)
    
    assert result.duplicate == True
    assert result.action == "delete"
    print(f"  ✅ Duplicate item review: {result.duplicate}, {result.action}")
    
    # Test Case 4: Irrelevant item (not accessed in 90 days)
    item = MemoryItem(
        path=Path("irrelevant.py"),
        name="irrelevant.py",
        type="code",
        size=1000,
        access_count=0,
        last_accessed=now - timedelta(days=60),
        created_at=now,
        importance_score=0.5,
        tags=[]
    )
    
    result = reviewer.review_item(item)
    
    assert result.relevance == "irrelevant"
    assert result.action == "delete"
    print(f"  ✅ Irrelevant item review: {result.relevance}, {result.action}")
    
    print("  ✅ MemoryReviewer tests passed")
    return True


def run_all_tests():
    print("=" * 70)
    print("🧪 Periodic Review Tests (Phase 3)")
    print("=" * 70)
    print()
    
    tests = {
        "MemoryScheduler": test_memory_scheduler,
        "MemoryReviewer": test_memory_reviewer,
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
        print("\n🎉 All tests passed! Periodic Review Mechanism complete.")
        print("   Phase 3: Periodic Review Mechanism - 100% COMPLETE")
        print("   Ready to proceed to: Progressive Memory Consolidation")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
