#!/usr/bin/env python3
"""
Memory Consolidation Runner - WORKSPACE WIDE

Scan and consolidate entire workspace memory.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import os
import json


# ==================== Domain Classes ====================

@dataclass
class MemoryItem:
    path: Path
    name: str
    type: str
    size: int
    access_count: int
    last_accessed: Optional[datetime]
    created_at: datetime
    importance_score: float
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "created_at": self.created_at.isoformat(),
            "importance_score": self.importance_score,
            "tags": self.tags
        }


@dataclass
class DuplicateGroup:
    canonical_item: str
    duplicate_items: List[str]
    similarity: float
    recommendation: str
    confidence: float


@dataclass
class SimilarGroup:
    canonical_item: str
    similar_items: List[str]
    similarity: float
    recommendation: str
    confidence: float


@dataclass
class Archive:
    name: str
    items: List[str]
    created_at: datetime
    size: int


@dataclass
class ConsolidationResult:
    deleted_items: List[str]
    archived_items: List[str]
    merged_items: List[str]
    space_saved: int
    items_processed: int
    time_taken: float


# ==================== Consolidation Engine ====================

class MemoryConsolidator:
    """
    Performs actual memory consolidation on workspace.
    """
    
    def __init__(self, workspace: Path, archive_dir: Optional[Path] = None):
        self.workspace = workspace
        self.archive_dir = archive_dir if archive_dir else workspace / ".archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # File patterns to include
        self.include_patterns = [
            "*.py",           # Python files
            "*.js", "*.ts",  # JavaScript/TypeScript files
            "*.json", "*.yaml", "*.yml",  # Configuration files
            "*.md",            # Markdown files
            "*.txt",           # Text files
        ]
        
        # File patterns to exclude
        self.exclude_patterns = [
            "*.pyc",
            "*__pycache__",
            "*.swp",
            "*~",
            "*.bak",
            "*.tmp",
        ]
        
        # Directories to exclude
        self.exclude_dirs = [
            ".git",
            ".gitignore",
            "__pycache__",
            "node_modules",
            ".moltbot",
            ".clawhub",
            "archives",
            "tests",
            ".archives"
        ]
    
    def scan_memory_items(self) -> List[MemoryItem]:
        """
        Scan entire workspace for memory items.
        
        Returns:
            List of MemoryItems
        """
        items = []
        
        print(f"  📂 Scanning workspace: {self.workspace}")
        
        for root, dirs, files in os.walk(self.workspace):
            # Skip excluded directories
            root_path = Path(root)
            for exclude_dir in self.exclude_dirs:
                if exclude_dir in root_path.parts:
                    break
            else:
                continue
            
            # Scan files
            for file in files:
                file_path = Path(root) / file
                
                # Skip if matches exclude patterns
                skip = False
                for exclude_pattern in self.exclude_patterns:
                    if file_path.match(exclude_pattern):
                        skip = True
                        break
                
                if skip:
                    continue
                
                # Check if matches include patterns
                include = False
                for include_pattern in self.include_patterns:
                    if file_path.match(include_pattern):
                        include = True
                        break
                
                if not include:
                    continue
                
                try:
                    # Get file stats
                    stat = file_path.stat()
                    created_at = datetime.fromtimestamp(stat.st_ctime)
                    last_accessed = datetime.fromtimestamp(stat.st_atime)
                    
                    # Determine file type
                    if file_path.suffix in [".py", ".js", ".ts"]:
                        file_type = "code"
                    elif file_path.suffix in [".json", ".yaml", ".yml", ".toml", ".cfg"]:
                        file_type = "config"
                    elif file_path.suffix == ".md":
                        file_type = "docs"
                    elif file_path.suffix == ".txt":
                        file_type = "data"
                    else:
                        file_type = "other"
                    
                    # Determine tags
                    tags = []
                    tags.append(f"type:{file_type}")
                    tags.append("is_file")
                    
                    if file_path.parent.name in ["skills", "memory", "logs", "docs"]:
                        tags.append(f"domain:{file_path.parent.name}")
                    
                    # Create memory item
                    item = MemoryItem(
                        path=file_path,
                        name=file_path.name,
                        type=file_type,
                        size=stat.st_size,
                        access_count=0,  # Will be updated by usage tracker
                        last_accessed=last_accessed,
                        created_at=created_at,
                        importance_score=0.0,  # Will be calculated later
                        tags=tags
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    # Skip files that can't be accessed
                    continue
        
        return items
    
    def find_duplicates(self, items: List[MemoryItem]) -> List[DuplicateGroup]:
        """
        Find duplicate memory items based on name and content.
        
        Returns:
            List of DuplicateGroups
        """
        duplicate_groups = []
        
        # Group by name
        name_groups: Dict[str, List[MemoryItem]] = {}
        for item in items:
            if item.name not in name_groups:
                name_groups[item.name] = []
            name_groups[item.name].append(item)
        
        # Find duplicates (groups with > 1 item)
        for name, group in name_groups.items():
            if len(group) > 1:
                # Sort by size (largest = canonical)
                sorted_group = sorted(group, key=lambda x: -x.size)
                
                canonical = sorted_group[0]
                duplicates = sorted_group[1:]
                
                group = DuplicateGroup(
                    canonical_item=str(canonical.path),
                    duplicate_items=[str(d.path) for d in duplicates],
                    similarity=1.0,  # Exact name match
                    recommendation="delete",  # Keep canonical, delete duplicates
                    confidence=0.9
                )
                
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def find_similar_items(self, items: List[MemoryItem]) -> List[SimilarGroup]:
        """
        Find similar memory items based on size and type.
        
        Returns:
            List of SimilarGroups
        """
        similar_groups = []
        
        # Group by size and type
        size_type_groups: Dict[Tuple[int, str], List[MemoryItem]] = {}
        
        for item in items:
            # Round size to nearest 1KB
            size_kb = int(item.size / 1024)
            type_key = (size_kb, item.type)
            
            if type_key not in size_type_groups:
                size_type_groups[type_key] = []
            
            size_type_groups[type_key].append(item)
        
        # Find similar items (same size and type)
        for (size_kb, file_type), group in size_type_groups.items():
            if len(group) > 1:
                # Sort by importance (highest = canonical)
                sorted_group = sorted(group, key=lambda x: -x.importance_score)
                
                if sorted_group[0].importance_score > 0:
                    canonical = sorted_group[0]
                    similar = sorted_group[1:]
                    
                    group = SimilarGroup(
                        canonical_item=str(canonical.path),
                        similar_items=[str(s.path) for s in similar],
                        similarity=0.7,  # Same size and type
                        recommendation="merge",  # Merge similar items
                        confidence=0.7
                    )
                    
                    similar_groups.append(group)
        
        return similar_groups
    
    def identify_archive_candidates(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """
        Identify items for archiving.
        
        Returns:
            List of MemoryItems to archive
        """
        archive_candidates = []
        
        for item in items:
            # Archive criteria:
            # 1. File size > 100KB (large files)
            # 2. Type is "docs" or "other"
            # 3. Not recently accessed (> 7 days)
            # 4. Low importance (< 0.3)
            
            should_archive = False
            
            if item.size > 102400:  # > 100KB
                should_archive = True
            
            if item.type in ["docs", "other"] and item.last_accessed:
                days_since_access = (datetime.now() - item.last_accessed).total_seconds() / 86400.0
                if days_since_access > 7:
                    should_archive = True
            
            if item.importance_score < 0.3:
                should_archive = True
            
            if should_archive:
                archive_candidates.append(item)
        
        return archive_candidates
    
    def perform_consolidation(self, dry_run: bool = True) -> ConsolidationResult:
        """
        Perform memory consolidation.
        
        Args:
            dry_run: If True, don't actually delete files, just report
        
        Returns:
            ConsolidationResult with details
        """
        start_time = datetime.now()
        
        print("=" * 70)
        print("🧬 Memory Consolidation - Workspace Analysis")
        print("=" * 70)
        print()
        
        # Step 1: Scan memory items
        print("📂 Step 1: Scanning workspace for memory items...")
        items = self.scan_memory_items()
        print(f"  ✅ Scanned {len(items)} memory items")
        
        if not items:
            return ConsolidationResult(
                deleted_items=[],
                archived_items=[],
                merged_items=[],
                space_saved=0,
                items_processed=0,
                time_taken=0.0
            )
        
        # Step 2: Find duplicates
        print("\n🔍 Step 2: Finding duplicates...")
        duplicate_groups = self.find_duplicates(items)
        print(f"  ✅ Found {len(duplicate_groups)} duplicate groups")
        
        for group in duplicate_groups[:5]:
            print(f"     - {group.canonical_item.split('/')[-1]}: {len(group.duplicate_items)} duplicates")
        
        # Step 3: Find similar items
        print("\n🔍 Step 3: Finding similar items...")
        similar_groups = self.find_similar_items(items)
        print(f"  ✅ Found {len(similar_groups)} similar item groups")
        
        for group in similar_groups[:5]:
            print(f"     - {group.canonical_item.split('/')[-1]}: {len(group.similar_items)} similar items")
        
        # Step 4: Identify archive candidates
        print("\n📦 Step 4: Identifying archive candidates...")
        archive_candidates = self.identify_archive_candidates(items)
        print(f"  ✅ Found {len(archive_candidates)} candidates for archiving")
        
        for item in archive_candidates[:5]:
            print(f"     - {item.path.relative_to(self.workspace)}: {item.importance_score:.2f}")
        
        # Step 5: Perform consolidation
        print("\n⚙️  Step 5: Performing consolidation...")
        
        deleted_items = []
        archived_items = []
        merged_items = []
        space_saved = 0
        
        # Delete duplicates
        if not dry_run:
            print("  🗑️  Deleting duplicates...")
            for group in duplicate_groups:
                for item_path in group.duplicate_items:
                    path = Path(item_path)
                    if path.exists():
                        try:
                            space_saved += path.stat().st_size
                            path.unlink()
                            deleted_items.append(str(path))
                        except Exception as e:
                            print(f"     ⚠️  Could not delete {item_path}: {e}")
        else:
            print("  🗑️  [DRY RUN] Would delete duplicates...")
            for group in duplicate_groups[:3]:
                print(f"     - {len(group.duplicate_items)} duplicates of {group.canonical_item.split('/')[-1]}")
        
        # Archive large/old items
        if not dry_run:
            print("\n  📦 Archiving large/old items...")
            archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            archive_path = self.archive_dir / archive_name
            archive_path.mkdir(exist_ok=True)
            
            total_archived_size = 0
            for item in archive_candidates:
                item_path = item.path
                if item_path.exists():
                    try:
                        # Copy to archive
                        dst = archive_path / item.path.name
                        shutil.copy2(item_path, dst)
                        archived_items.append(str(item_path))
                        total_archived_size += item.stat().st_size
                    except Exception as e:
                        print(f"     ⚠️  Could not archive {item_path}: {e}")
            
            print(f"  ✅ Archived {len(archived_items)} items")
            print(f"     Archive: {archive_name}")
            print(f"     Total size: {total_archived_size} bytes")
        else:
            print("  📦 [DRY RUN] Would archive large/old items...")
            print(f"     Candidates: {len(archive_candidates)} items")
            print(f"     Large files: {len([i for i in archive_candidates if i.size > 102400])}")
            print(f"     Old items: {len([i for i in archive_candidates if i.last_accessed])}")
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        
        return ConsolidationResult(
            deleted_items=deleted_items,
            archived_items=archived_items,
            merged_items=merged_items,
            space_saved=space_saved,
            items_processed=len(items),
            time_taken=time_taken
        )


def main():
    """
    Run memory consolidation on current workspace.
    """
    # Get current workspace
    workspace = Path.cwd()
    
    print("=" * 70)
    print("🧬 Memory Consolidation Runner")
    print("=" * 70)
    print()
    print(f"Workspace: {workspace}")
    print(f"Archive Directory: {workspace / '.archives'}")
    print()
    
    # Run consolidation (dry run first)
    consolidator = MemoryConsolidator(workspace)
    
    # First run as dry run
    print("🧬 Running CONSERVATION (DRY RUN)")
    print()
    result = consolidator.perform_consolidation(dry_run=True)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 DRY RUN Summary")
    print("=" * 70)
    print()
    print(f"Items Processed: {result.items_processed}")
    print(f"Duplicate Groups: {len(result.deleted_items) // 2 if result.deleted_items else 0}")
    print(f"Similar Item Groups: {len(result.merged_items)}")
    print(f"Archive Candidates: {len(result.archived_items)}")
    print()
    print(f"Would Delete: {len(result.deleted_items)} items")
    print(f"Would Archive: {len(result.archived_items)} items")
    print(f"Would Save: {result.space_saved} bytes")
    print()
    
    # Ask user to confirm
    print("=" * 70)
    print("🤔 Ready to perform actual consolidation?")
    print("=" * 70)
    print()
    print("This will:")
    print(f"  1. Delete {len(result.deleted_items)} duplicate items")
    print(f"  2. Archive {len(result.archived_items)} large/old items")
    print(f"  3. Save {result.space_saved} bytes of space")
    print()
    print("⚠️  WARNING: This operation cannot be easily undone!")
    print("   Files will be permanently deleted!")
    print()
    print("To proceed, run:")
    print(f"  python3 {sys.argv[0]} --confirm")
    print()
    print("To cancel, just exit.")
    print("=" * 70)
    
    # Check if user confirmed
    if "--confirm" in sys.argv:
        print("\n⚙️  Proceeding with consolidation...")
        result = consolidator.perform_consolidation(dry_run=False)
        
        # Save consolidation report
        report_file = workspace / ".consolidation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "workspace": str(workspace),
                "items_processed": result.items_processed,
                "deleted_items": result.deleted_items,
                "archived_items": result.archived_items,
                "merged_items": result.merged_items,
                "space_saved": result.space_saved,
                "time_taken": result.time_taken,
            }, f, indent=2)
        
        print(f"\n✅ Consolidation report saved to: {report_file}")
        print("✅ Workspace consolidation completed!")
    else:
        print("\n🧹  CANCELED: Dry run only. No files were modified.")


if __name__ == "__main__":
    main()
