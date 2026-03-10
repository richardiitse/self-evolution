"""
Periodic Review Mechanism

Implements automatic memory review and evaluation.

Components:
- MemoryScheduler - Schedule periodic memory reviews
- MemoryReviewer - Perform memory reviews
- ReviewResult - Review result
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import math


@dataclass
class ReviewSchedule:
    """
    Represents a review schedule.
    
    Attributes:
        - review_type: Type of review (daily, weekly, monthly)
        - items: Items to review
        - scheduled_time: When to perform review
        - frequency: Review frequency in hours
    """
    review_type: str
    items: List[str]
    scheduled_time: datetime
    frequency: int  # hours


@dataclass
class ReviewResult:
    """
    Result of a memory review.
    
    Attributes:
        - item_path: Path to memory item
        - item_name: Name of memory item
        - relevance: Whether item is still relevant
        - importance_changed: Whether importance score changed
        - new_importance: New importance score (if changed)
        - outdated: Whether item is outdated
        - duplicate: Whether item is duplicate
        - action: Recommended action (keep, archive, delete, consolidate)
        - confidence: Confidence in review result (0.0 - 1.0)
        - review_time: When review was performed
    """
    item_path: str
    item_name: str
    relevance: str  # "relevant", "potentially_irrelevant", "irrelevant"
    importance_changed: bool
    new_importance: float
    outdated: bool
    duplicate: bool
    action: str  # "keep", "archive", "delete", "consolidate"
    confidence: float
    review_time: datetime


class MemoryScheduler:
    """
    Schedule periodic memory reviews.
    
    Scheduling Options:
    - Daily review (for critical items)
    - Weekly review (for important items)
    - Monthly review (for all items)
    - Event-driven review (when significant changes occur)
    """
    
    def __init__(self):
        self.daily_interval = 24  # hours
        self.weekly_interval = 168  # hours (7 days)
        self.monthly_interval = 720  # hours (30 days)
        
        self.review_priorities = {
            "critical": {"interval": self.daily_interval, "importance": 0.8},
            "high": {"interval": self.weekly_interval, "importance": 0.6},
            "medium": {"interval": self.monthly_interval, "importance": 0.4},
            "low": {"interval": self.monthly_interval, "importance": 0.2},
        }
    
    def schedule_review(self, items: List[Dict[str, Any]], 
                     frequency: str = "medium") -> ReviewSchedule:
        """
        Schedule a review for memory items.
        
        Args:
            items: List of memory items (with importance_score)
            frequency: Review frequency ("daily", "weekly", "monthly", "critical")
        
        Returns:
            ReviewSchedule
        """
        if not items:
            return ReviewSchedule(
                review_type=frequency,
                items=[],
                scheduled_time=datetime.now() + timedelta(hours=self.review_priorities.get(frequency, {}).get("interval", 720)),
                frequency=self.review_priorities.get(frequency, {}).get("interval", 720)
            )
        
        # Determine interval
        if frequency in self.review_priorities:
            interval_hours = self.review_priorities[frequency]["interval"]
        else:
            interval_hours = self.monthly_interval
        
        # Filter items by importance threshold
        min_importance = self.review_priorities.get(frequency, {}).get("importance", 0.4)
        filtered_items = [
            item["path"] if isinstance(item, dict) else str(item)
            for item in items
            if item.get("importance_score", 0.0) >= min_importance
        ]
        
        # Schedule for next interval
        scheduled_time = datetime.now() + timedelta(hours=interval_hours)
        
        return ReviewSchedule(
            review_type=frequency,
            items=filtered_items,
            scheduled_time=scheduled_time,
            frequency=interval_hours
        )
    
    def schedule_daily_reviews(self, critical_items: List[Dict[str, Any]]) -> ReviewSchedule:
        """Schedule daily reviews for critical items."""
        return self.schedule_review(critical_items, frequency="critical")
    
    def schedule_weekly_reviews(self, important_items: List[Dict[str, Any]]) -> ReviewSchedule:
        """Schedule weekly reviews for important items."""
        return self.schedule_review(important_items, frequency="high")
    
    def schedule_monthly_reviews(self, all_items: List[Dict[str, Any]]) -> ReviewSchedule:
        """Schedule monthly reviews for all items."""
        return self.schedule_review(all_items, frequency="medium")
    
    def get_next_review_time(self, schedule: ReviewSchedule) -> datetime:
        """Get next review time from schedule."""
        return schedule.scheduled_time
    
    def is_review_due(self, schedule: ReviewSchedule) -> bool:
        """Check if a review is due."""
        return datetime.now() >= schedule.scheduled_time


class MemoryReviewer:
    """
    Perform memory review based on schedule.
    
    Review Tasks:
    - Check if content is still relevant
    - Check if importance score has changed
    - Check for outdated information
    - Check for duplicates
    - Check for conflicting information
    """
    
    def __init__(self):
        self.relevance_threshold = 0.3  # Below this is irrelevant
        self.outdated_threshold_days = 90  # 90 days = outdated
        self.duplicate_similarity_threshold = 0.9  # 90% similarity = duplicate
        
        # Action priorities
        self.action_priorities = {
            "delete": 1,
            "archive": 0.8,
            "consolidate": 0.7,
            "keep": 0.5,
        }
    
    def review_item(self, item_path: Path, item_metadata: Dict[str, Any]) -> ReviewResult:
        """
        Review a single memory item.
        
        Args:
            item_path: Path to memory file/directory
            item_metadata: Metadata about the item
        
        Returns:
            ReviewResult with evaluation and action recommendation
        """
        # Initialize review result
        review_time = datetime.now()
        
        # Extract metadata
        importance_score = item_metadata.get("importance_score", 0.5)
        last_accessed = item_metadata.get("last_accessed")
        created_at = item_metadata.get("created_at")
        size = item_metadata.get("size", 0)
        tags = item_metadata.get("tags", [])
        
        # 1. Check relevance
        relevance = self._check_relevance(item_path, item_metadata)
        
        # 2. Check if outdated
        outdated = self._check_outdated(created_at, last_accessed)
        
        # 3. Check if duplicate
        duplicate = self._check_duplicate(item_path, item_metadata)
        
        # 4. Calculate new importance (if changed)
        importance_changed, new_importance = self._recalculate_importance(item_path, item_metadata)
        
        # 5. Determine action
        action = self._determine_action(relevance, outdated, duplicate, importance_score, new_importance)
        
        # 6. Calculate confidence
        confidence = self._calculate_confidence(relevance, outdated, duplicate, importance_changed)
        
        return ReviewResult(
            item_path=str(item_path),
            item_name=item_path.name,
            relevance=relevance,
            importance_changed=importance_changed,
            new_importance=new_importance if importance_changed else importance_score,
            outdated=outdated,
            duplicate=duplicate,
            action=action,
            confidence=confidence,
            review_time=review_time
        )
    
    def _check_relevance(self, item_path: Path, metadata: Dict[str, Any]) -> str:
        """
        Check if content is still relevant.
        
        Returns: "relevant", "potentially_irrelevant", or "irrelevant"
        """
        # Check recency
        last_accessed = metadata.get("last_accessed")
        if last_accessed is None:
            # Never accessed - can't determine relevance
            return "potentially_irrelevant"
        
        days_since_access = (datetime.now() - last_accessed).total_seconds() / 86400.0
        
        # Check if recently accessed
        if days_since_access < 7:  # Within last week
            return "relevant"
        elif days_since_access < 30:  # Within last month
            return "potentially_irrelevant"
        else:
            # Accessed long ago
            return "irrelevant"
    
    def _check_outdated(self, created_at: datetime, last_accessed: Optional[datetime]) -> bool:
        """
        Check if information is outdated.
        
        Returns: True if outdated, False otherwise
        """
        # Check if created long ago and never accessed recently
        if created_at:
            days_since_creation = (datetime.now() - created_at).total_seconds() / 86400.0
            
            if days_since_creation > self.outdated_threshold_days:
                if last_accessed is None:
                    return True
                
                days_since_access = (datetime.now() - last_accessed).total_seconds() / 86400.0
                if days_since_access > 30:  # Not accessed in last month
                    return True
        
        return False
    
    def _check_duplicate(self, item_path: Path, metadata: Dict[str, Any]) -> bool:
        """
        Check if item is duplicate.
        
        For MVP, we'll use a simple check based on size and tags.
        """
        # Check for duplicate indicators in tags
        duplicate_indicators = [tag for tag in metadata.get("tags", []) if tag.startswith("duplicate:")]
        
        return len(duplicate_indicators) > 0
    
    def _recalculate_importance(self, item_path: Path, metadata: Dict[str, Any]) -> tuple[bool, float]:
        """
        Recalculate importance score.
        
        Returns: (importance_changed, new_importance_score)
        """
        # Get current importance
        current_importance = metadata.get("importance_score", 0.5)
        
        # Get access count (if tracked)
        access_count = metadata.get("access_count", 0)
        
        # Recalculate based on recent access
        if access_count > 10:
            # Frequently accessed - higher importance
            new_importance = min(current_importance + 0.1, 1.0)
            return (True, new_importance)
        elif access_count == 0:
            # Never accessed - lower importance
            new_importance = max(current_importance - 0.1, 0.0)
            return (True, new_importance)
        else:
            # No significant change
            return (False, current_importance)
    
    def _determine_action(self, relevance: str, outdated: bool, 
                         duplicate: bool, current_importance: float,
                         new_importance: float) -> str:
        """
        Determine recommended action.
        
        Returns: "keep", "archive", "delete", or "consolidate"
        """
        # Priority 1: Delete duplicates
        if duplicate:
            return "delete"
        
        # Priority 2: Delete irrelevant items
        if relevance == "irrelevant":
            return "delete"
        
        # Priority 3: Archive outdated items
        if outdated:
            return "archive"
        
        # Priority 4: Archive low-importance items
        if new_importance < self.relevance_threshold:
            return "archive"
        
        # Priority 5: Keep relevant items
        if relevance == "relevant" or relevance == "potentially_irrelevant":
            return "keep"
        
        # Default: Keep
        return "keep"
    
    def _calculate_confidence(self, relevance: str, outdated: bool,
                            duplicate: bool, importance_changed: bool) -> float:
        """
        Calculate confidence in review result.
        
        Returns: Confidence score (0.0 - 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Adjust based on relevance
        if relevance == "relevant":
            confidence += 0.2
        elif relevance == "irrelevant":
            confidence -= 0.2
        else:  # potentially_irrelevant
            confidence += 0.0
        
        # Adjust based on outdated status
        if outdated:
            confidence += 0.1
        else:
            confidence -= 0.05
        
        # Adjust based on duplicate status
        if duplicate:
            confidence += 0.2  # Duplicate is clear
        else:
            confidence -= 0.1
        
        # Clamp to 0.0 - 1.0
        return max(0.0, min(1.0, confidence))
    
    def review_batch(self, items: List[Dict[str, Any]]) -> List[ReviewResult]:
        """
        Review a batch of memory items.
        
        Args:
            items: List of memory items with metadata
        
        Returns:
            List of ReviewResults
        """
        results = []
        
        for item in items:
            item_path = Path(item.get("path", ""))
            if not item_path.exists():
                continue
            
            # Create result with basic metadata if review fails
            try:
                result = self.review_item(item_path, item)
                results.append(result)
            except Exception as e:
                # Fallback result
                results.append(ReviewResult(
                    item_path=str(item_path),
                    item_name=item_path.name,
                    relevance="unknown",
                    importance_changed=False,
                    new_importance=0.0,
                    outdated=False,
                    duplicate=False,
                    action="keep",  # Safe default
                    confidence=0.3,  # Low confidence
                    review_time=datetime.now()
                ))
        
        return results
    
    def update_importance_scores(self, items: List[Dict[str, Any]], 
                              review_results: List[ReviewResult]) -> List[Dict[str, Any]]:
        """
        Update importance scores based on review results.
        
        Args:
            items: Original items
            review_results: Review results
        
        Returns:
            Updated items with new importance scores
        """
        updated_items = []
        
        for item in items:
            item_path = item.get("path", "")
            
            # Find corresponding review result
            for result in review_results:
                if result.item_path == item_path:
                    # Update importance score if changed
                    if result.importance_changed:
                        item["importance_score"] = result.new_importance
                        item["last_reviewed"] = datetime.now().isoformat()
                    
                    # Add review metadata
                    item["relevance"] = result.relevance
                    item["outdated"] = result.outdated
                    item["duplicate"] = result.duplicate
                    item["recommended_action"] = result.action
                    item["review_confidence"] = result.confidence
                    
                    updated_items.append(item)
                    break
            else:
                # No review result for this item
                updated_items.append(item)
        
        return updated_items
    
    def identify_archived_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify items that should be archived.
        
        Returns:
            List of items that should be archived
        """
        archived_items = []
        
        for item in items:
            item_path = item.get("path", "")
            
            # Find corresponding review result
            for result in self.review_batch(items):
                if result.item_path == item_path:
                    # Check if should be archived
                    if result.action in ["archive", "delete"]:
                        item["archive_reason"] = result.relevance
                        item["archive_date"] = datetime.now().isoformat()
                        archived_items.append(item)
                    break
        
        return archived_items
