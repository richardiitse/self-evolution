"""
Progressive Memory Consolidation

Implements memory consolidation, archiving, and deduplication.

Components:
- MemoryConsolidator - Consolidate memory items
- ArchiveManager - Manage memory archives
- DuplicateFinder - Find duplicate items
- SimilarityFinder - Find similar items
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import shutil
import os


@dataclass
class DuplicateGroup:
    """
    Represents a group of duplicate memory items.
    
    Attributes:
        - canonical_item: The primary item to keep
        - duplicate_items: List of duplicate items
        - similarity: Similarity score (0.0 - 1.0)
        - recommendation: Action to take
    """
    canonical_item: str  # Path to canonical item
    duplicate_items: List[str]  # Paths to duplicate items
    similarity: float
    recommendation: str  # "keep", "merge", "delete"
    confidence: float


@dataclass
class SimilarGroup:
    """
    Represents a group of similar memory items.
    
    Attributes:
        - canonical_item: The primary item to keep
        - similar_items: List of similar items
        - similarity: Average similarity score
        - common_features: List of common features
        - recommendation: Action to take
    """
    canonical_item: str  # Path to canonical item
    similar_items: List[str]  # Paths to similar items
    similarity: float
    common_features: List[str]
    recommendation: str  # "keep", "merge", "consolidate"
    confidence: float


@dataclass
class Archive:
    """
    Represents a memory archive.
    
    Attributes:
        - name: Archive name
        - items: Items in archive
        - created_at: Archive creation time
        - size: Archive size in bytes
        - compressed: Whether archive is compressed
        - index: Archive index
    """
    name: str
    items: List[str]  # Paths to archived items
    created_at: datetime
    size: int
    compressed: bool
    index: Dict[str, Dict[str, Any]]  # Path -> metadata


@dataclass
class ConsolidationResult:
    """
    Result of memory consolidation.
    
    Attributes:
        - deleted_items: Items deleted
        - archived_items: Items archived
        - merged_items: Items merged
        - space_saved: Space saved (bytes)
        - time_taken: Time taken (seconds)
    """
    deleted_items: List[str]
    archived_items: List[str]
    merged_items: List[str]
    space_saved: int
    time_taken: float


class DuplicateFinder:
    """
    Find duplicate memory items.
    
    Detection Methods:
    - Content-based: Compare file content
    - Name-based: Compare file names
    - Metadata-based: Compare metadata (size, type, tags)
    """
    
    def __init__(self):
        self.content_similarity_threshold = 0.9
        self.name_similarity_threshold = 0.8
    
    def find_duplicates_by_name(self, items: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """
        Find duplicates based on file names.
        
        Args:
            items: List of memory items with "name" field
        
        Returns:
            List of DuplicateGroups
        """
        # Group items by name
        name_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for item in items:
            name = item.get("name", "")
            if not name:
                continue
            
            if name not in name_groups:
                name_groups[name] = []
            
            name_groups[name].append(item)
        
        # Find duplicates (groups with > 1 item)
        duplicate_groups = []
        
        for name, group in name_groups.items():
            if len(group) > 1:
                # Sort by importance score (highest first)
                sorted_group = sorted(group, key=lambda x: x.get("importance_score", 0.5), reverse=True)
                
                # Canonical item = highest importance
                canonical = sorted_group[0]
                duplicates = sorted_group[1:]
                
                # Calculate similarity (1.0 for exact name match)
                similarity = 1.0
                
                # Recommendation: Keep canonical, delete duplicates
                recommendation = "delete"
                
                group = DuplicateGroup(
                    canonical_item=canonical.get("path", ""),
                    duplicate_items=[d.get("path", "") for d in duplicates],
                    similarity=similarity,
                    recommendation=recommendation,
                    confidence=0.9
                )
                
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def find_duplicates_by_content(self, items: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """
        Find duplicates based on file content.
        
        Args:
            items: List of memory items with "path" field
        
        Returns:
            List of DuplicateGroups
        """
        # Group items by content hash
        content_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for item in items:
            path = item.get("path", "")
            if not path or not Path(path).exists():
                continue
            
            try:
                # Read file content
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Calculate simple content hash
                content_hash = hash(content)
                
                if content_hash not in content_groups:
                    content_groups[content_hash] = []
                
                content_groups[content_hash].append(item)
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Find duplicates (groups with > 1 item)
        duplicate_groups = []
        
        for content_hash, group in content_groups.items():
            if len(group) > 1:
                # Sort by importance score (highest first)
                sorted_group = sorted(group, key=lambda x: x.get("importance_score", 0.5), reverse=True)
                
                # Canonical item = highest importance
                canonical = sorted_group[0]
                duplicates = sorted_group[1:]
                
                # Calculate similarity (exact content match = 1.0)
                similarity = 1.0
                
                # Recommendation: Keep canonical, delete duplicates
                recommendation = "delete"
                
                group = DuplicateGroup(
                    canonical_item=canonical.get("path", ""),
                    duplicate_items=[d.get("path", "") for d in duplicates],
                    similarity=similarity,
                    recommendation=recommendation,
                    confidence=1.0  # Exact match
                )
                
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def find_duplicates_by_metadata(self, items: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """
        Find duplicates based on metadata (size, type, tags).
        
        Args:
            items: List of memory items with metadata
        
        Returns:
            List of DuplicateGroups
        """
        # Group items by type + size
        metadata_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for item in items:
            item_type = item.get("type", "other")
            size = item.get("size", 0)
            
            # Create key: type_size (e.g., "code_1000")
            if size < 1000:
                size_bucket = "small"
            elif size < 10000:
                size_bucket = "medium"
            else:
                size_bucket = "large"
            
            key = f"{item_type}_{size_bucket}"
            
            if key not in metadata_groups:
                metadata_groups[key] = []
            
            metadata_groups[key].append(item)
        
        # Find duplicates (groups with > 1 item)
        duplicate_groups = []
        
        for key, group in metadata_groups.items():
            if len(group) > 1:
                # Sort by importance score (highest first)
                sorted_group = sorted(group, key=lambda x: x.get("importance_score", 0.5), reverse=True)
                
                # Canonical item = highest importance
                canonical = sorted_group[0]
                duplicates = sorted_group[1:]
                
                # Calculate similarity (exact metadata match = 0.9)
                similarity = 0.9
                
                # Recommendation: Keep canonical, consider merging
                recommendation = "merge"
                
                group = DuplicateGroup(
                    canonical_item=canonical.get("path", ""),
                    duplicate_items=[d.get("path", "") for d in duplicates],
                    similarity=similarity,
                    recommendation=recommendation,
                    confidence=0.8
                )
                
                duplicate_groups.append(group)
        
        return duplicate_groups


class SimilarityFinder:
    """
    Find similar memory items.
    
    Similarity Metrics:
    - Name similarity (edit distance)
    - Content similarity (cosine similarity of word counts)
    - Metadata similarity (type, tags)
    """
    
    def __init__(self):
        self.name_similarity_threshold = 0.7
        self.content_similarity_threshold = 0.8
        self.metadata_similarity_threshold = 0.6
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate name similarity using edit distance.
        
        Args:
            name1: First name
            name2: Second name
        
        Returns:
            Similarity score (0.0 - 1.0)
        """
        # Normalize names
        norm1 = name1.lower().replace("_", "").replace("-", "").replace(" ", "")
        norm2 = name2.lower().replace("_", "").replace("-", "").replace(" ", "")
        
        # Calculate edit distance
        if norm1 == norm2:
            return 1.0
        
        # Simple edit distance
        len1, len2 = len(norm1), len(norm2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        
        for j in range(1, len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0
                if norm1[i - 1] == norm2[j - 1]:
                    cost = matrix[i - 1][j]
                else:
                    cost = min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i][j + 1] + 1)
                matrix[i][j] = cost
        
        similarity = 1.0 - (matrix[len1)][len2] / (len1 + len2))
        
        return similarity
    
    def calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate content similarity using word frequencies.
        
        Args:
            content1: First content
            content2: Second content
        
        Returns:
            Similarity score (0.0 - 1.0)
        """
        # Tokenize into words
        words1 = content1.lower().split()
        words2 = content2.lower().split()
        
        # Create word frequency maps
        freq1 = {}
        freq2 = {}
        
        for word in words1:
            freq1[word] = freq1.get(word, 0) + 1
        
        for word in words2:
            freq2[word] = freq2.get(word, 0) + 1
        
        # Calculate cosine similarity
        all_words = set(freq1.keys()).union(set(freq2.keys()))
        
        dot_product = 0.0
        norm1_sq = 0.0
        norm2_sq = 0.0
        
        for word in all_words:
            f1 = freq1.get(word, 0)
            f2 = freq2.get(word, 0)
            
            dot_product += f1 * f2
            norm1_sq += f1 ** 2
            norm2_sq += f2 ** 2
        
        if norm1_sq == 0 or norm2_sq == 0:
            return 0.0
        
        similarity = dot_product / ((norm1_sq ** 0.5) * (norm2_sq ** 0.5))
        
        return similarity
    
    def find_similar_items(self, items: List[Dict[str, Any]], 
                           threshold: float = 0.7) -> List[SimilarGroup]:
        """
        Find similar items based on name and content.
        
        Args:
            items: List of memory items
            threshold: Similarity threshold (0.0 - 1.0)
        
        Returns:
            List of SimilarGroups
        """
        similar_groups = []
        
        for i, item1 in enumerate(items):
            name1 = item1.get("name", "")
            path1 = item1.get("path", "")
            
            if not path1 or not Path(path1).exists():
                continue
            
            # Read content for similarity check
            try:
                with open(path1, 'r', encoding='utf-8') as f:
                    content1 = f.read()
            except:
                continue
            
            # Compare with other items
            for j, item2 in enumerate(items):
                if i >= j:
                    continue  # Don't compare with itself or already compared
                
                name2 = item2.get("name", "")
                path2 = item2.get("path", "")
                
                if not path2 or not Path(path2).exists():
                    continue
                
                # Calculate name similarity
                name_similarity = self.calculate_name_similarity(name1, name2)
                
                # Read content for similarity check
                try:
                    with open(path2, 'r', encoding='utf-8') as f:
                        content2 = f.read()
                except:
                    continue
                
                # Calculate content similarity
                content_similarity = self.calculate_content_similarity(content1, content2)
                
                # Calculate metadata similarity
                item1_type = item1.get("type", "other")
                item2_type = item2.get("type", "other")
                metadata_similarity = 1.0 if item1_type == item2_type else 0.0
                
                # Check if above threshold
                avg_similarity = (name_similarity + content_similarity + metadata_similarity) / 3.0
                
                if avg_similarity >= threshold:
                    # Determine common features
                    common_features = []
                    if name_similarity > 0.8:
                        common_features.append("similar_name")
                    if content_similarity > 0.8:
                        common_features.append("similar_content")
                    if metadata_similarity == 1.0:
                        common_features.append("same_type")
                    
                    # Recommendation: Keep one, consider merging
                    recommendation = "consolidate" if avg_similarity > 0.9 else "keep"
                    confidence = min(avg_similarity + 0.1, 1.0)
                    
                    group = SimilarGroup(
                        canonical_item=item1.get("path", ""),
                        similar_items=[item2.get("path", "")],
                        similarity=avg_similarity,
                        common_features=common_features,
                        recommendation=recommendation,
                        confidence=confidence
                    )
                    
                    similar_groups.append(group)
        
        return similar_groups


class ArchiveManager:
    """
    Manage memory archives.
    
    Features:
    - Create archive from items
    - Compress archive
    - Restore from archive
    - Search archive
    - Update index
    """
    
    def __init__(self, archive_dir: Optional[Path] = None):
        self.archive_dir = archive_dir if archive_dir else Path.home() / ".clawhub" / "archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def create_archive(self, items: List[Dict[str, Any]], 
                    name: str = None) -> Archive:
        """
        Create an archive from memory items.
        
        Args:
            items: List of memory items to archive
            name: Archive name (optional)
        
        Returns:
            Archive object
        """
        # Filter existing items
        existing_items = [item for item in items if Path(item.get("path", "")).exists()]
        
        if not existing_items:
            return None
        
        # Generate archive name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = name or f"archive_{timestamp}"
        
        # Create archive directory
        archive_path = self.archive_dir / archive_name
        archive_path.mkdir(exist_ok=True)
        
        # Copy items to archive
        archived_items = []
        total_size = 0
        
        for item in existing_items:
            item_path = item.get("path", "")
            if not item_path:
                continue
            
            src = Path(item_path)
            dst = archive_path / src.name
            
            try:
                if src.is_file():
                    shutil.copy2(src, dst)
                    total_size += src.stat().st_size
                    archived_items.append(str(dst))
                elif src.is_dir():
                    shutil.copytree(src, dst)
                    total_size += sum(f.stat().st_size for f in src.rglob("*") if f.is_file())
                    archived_items.append(str(dst))
            except Exception as e:
                continue
        
        # Create archive
        archive = Archive(
            name=archive_name,
            items=archived_items,
            created_at=datetime.now(),
            size=total_size,
            compressed=False,
            index={}
        )
        
        return archive
    
    def compress_archive(self, archive: Archive) -> Archive:
        """
        Compress an archive.
        
        Args:
            archive: Archive to compress
        
        Returns:
            Compressed Archive object
        """
        archive_path = self.archive_dir / archive.name
        
        # Create compressed version
        compressed_name = f"{archive.name}_compressed"
        compressed_path = self.archive_dir / compressed_name
        compressed_path.mkdir(exist_ok=True)
        
        # Copy and compress files
        archived_items = []
        total_size = 0
        
        for item_path in archive.items:
            src = Path(item_path)
            dst = compressed_path / src.name
            
            try:
                if src.is_file():
                    # Copy file
                    shutil.copy2(src, dst)
                    # Compress (simplified: just copy for now)
                    total_size += src.stat().st_size
                    archived_items.append(str(dst))
                elif src.is_dir():
                    # Copy directory
                    shutil.copytree(src, dst)
                    # Could compress here
                    total_size += sum(f.stat().st_size for f in src.rglob("*") if f.is_file())
                    archived_items.append(str(dst))
            except Exception as e:
                continue
        
        # Update archive
        compressed_archive = Archive(
            name=compressed_name,
            items=archived_items,
            created_at=datetime.now(),
            size=total_size,
            compressed=True,
            index=archive.index.copy()
        )
        
        return compressed_archive
    
    def update_index(self, archive: Archive):
        """
        Update archive index.
        
        Args:
            archive: Archive to update
        """
        archive.index["name"] = archive.name
        archive.index["created_at"] = archive.created_at.isoformat()
        archive.index["size"] = archive.size
        archive.index["compressed"] = archive.compressed
        archive.index["items"] = archive.items
    
    def restore_from_archive(self, archive_name: str, item_name: str,
                           restore_to: Path) -> Path:
        """
        Restore an item from archive.
        
        Args:
            archive_name: Archive name
            item_name: Item name
            restore_to: Destination path
        
        Returns:
            Path to restored item
        """
        archive_path = self.archive_dir / archive_name
        item_path = archive_path / item_name
        
        if not item_path.exists():
            raise FileNotFoundError(f"Item {item_name} not found in archive {archive_name}")
        
        restore_to.mkdir(parents=True, exist_ok=True)
        dst = restore_to / item_name
        
        # Copy item back
        if item_path.is_file():
            shutil.copy2(item_path, dst)
        elif item_path.is_dir():
            shutil.copytree(item_path, dst)
        
        return dst
    
    def search_archives(self, query: str) -> List[str]:
        """
        Search archives for items matching query.
        
        Args:
            query: Search query
        
        Returns:
            List of matching item paths
        """
        results = []
        
        # Search in all archives
        for archive_dir in self.archive_dir.iterdir():
            if not archive_dir.is_dir():
                continue
            
            index_file = archive_dir / "index.json"
            
            if not index_file.exists():
                continue
            
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                
                    # Search in items
                    for item_path in index.get("items", []):
                        item_name = Path(item_path).name
                        
                        # Simple search in name
                        if query.lower() in item_name.lower():
                            results.append(str(item_path))
            except Exception as e:
                continue
        
        return results
    
    def get_archive_size(self, archive: Archive) -> int:
        """
        Get archive size in bytes.
        
        Args:
            archive: Archive
        
        Returns:
            Size in bytes
        """
        return archive.size


class MemoryConsolidator:
    """
    Consolidate memory items.
    
    Consolidation Strategies:
    - Delete duplicates
    - Archive old/unused items
    - Merge similar items
    - Compress large files
    """
    
    def __init__(self, duplicate_finder: DuplicateFinder = None,
                 similarity_finder: SimilarityFinder = None,
                 archive_manager: ArchiveManager = None):
        self.duplicate_finder = duplicate_finder or DuplicateFinder()
        self.similarity_finder = similarity_finder or SimilarityFinder()
        self.archive_manager = archive_manager or ArchiveManager()
    
    def find_duplicates(self, items: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """
        Find all duplicate items.
        
        Args:
            items: List of memory items
        
        Returns:
            List of DuplicateGroups
        """
        duplicate_groups = []
        
        # Find duplicates by name
        name_groups = self.duplicate_finder.find_duplicates_by_name(items)
        duplicate_groups.extend(name_groups)
        
        # Find duplicates by content (for small files only)
        small_items = [item for item in items if item.get("size", 0) < 10000]
        content_groups = self.duplicate_finder.find_duplicates_by_content(small_items)
        duplicate_groups.extend(content_groups)
        
        # Find duplicates by metadata
        metadata_groups = self.duplicate_finder.find_duplicates_by_metadata(items)
        duplicate_groups.extend(metadata_groups)
        
        return duplicate_groups
    
    def find_similar_items(self, items: List[Dict[str, Any]], 
                           threshold: float = 0.7) -> List[SimilarGroup]:
        """
        Find similar items.
        
        Args:
            items: List of memory items
            threshold: Similarity threshold
        
        Returns:
            List of SimilarGroups
        """
        return self.similarity_finder.find_similar_items(items, threshold)
    
    def consolidate_duplicates(self, duplicate_groups: List[DuplicateGroup]) -> ConsolidationResult:
        """
        Consolidate duplicate items.
        
        Args:
            duplicate_groups: List of duplicate groups
        
        Returns:
            ConsolidationResult
        """
        start_time = datetime.now()
        
        deleted_items = []
        archived_items = []
        merged_items = []
        space_saved = 0
        
        # Process each group
        for group in duplicate_groups:
            canonical_item = group.canonical_item
            duplicates = group.duplicate_items
            
            # Delete duplicates based on recommendation
            if group.recommendation == "delete":
                for item_path in duplicates:
                    try:
                        path = Path(item_path)
                        if path.exists():
                            space_saved += path.stat().st_size
                            path.unlink()
                            deleted_items.append(item_path)
                    except Exception as e:
                        continue
            
            elif group.recommendation == "archive":
                # Archive duplicates
                archive = self.archive_manager.create_archive(
                    [{"path": item_path} for item_path in duplicates]
                )
                
                if archive:
                    archived_items.extend(archive.items)
                    self.archive_manager.update_index(archive)
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        
        return ConsolidationResult(
            deleted_items=deleted_items,
            archived_items=archived_items,
            merged_items=merged_items,
            space_saved=space_saved,
            time_taken=time_taken
        )
    
    def consolidate_similar(self, similar_groups: List[SimilarGroup]) -> ConsolidationResult:
        """
        Consolidate similar items.
        
        Args:
            similar_groups: List of similar groups
        
        Returns:
            ConsolidationResult
        """
        start_time = datetime.now()
        
        archived_items = []
        merged_items = []
        space_saved = 0
        
        # Process each group
        for group in similar_groups:
            canonical_item = group.canonical_item
            similar_items = group.similar_items
            
            # Archive similar items
            if group.recommendation == "consolidate":
                archive = self.archive_manager.create_archive(
                    [{"path": item_path} for item_path in similar_items]
                )
                
                if archive:
                    archived_items.extend(archive.items)
                    self.archive_manager.update_index(archive)
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        
        return ConsolidationResult(
            deleted_items=[],
            archived_items=archived_items,
            merged_items=merged_items,
            space_saved=space_saved,
            time_taken=time_taken
        )
    
    def archive_old_items(self, items: List[Dict[str, Any]], 
                       days_threshold: int = 90) -> ConsolidationResult:
        """
        Archive old/unused items.
        
        Args:
            items: List of memory items
            days_threshold: Age threshold in days
        
        Returns:
            ConsolidationResult
        """
        start_time = datetime.now()
        
        old_items = []
        now = datetime.now()
        
        # Find old items
        for item in items:
            last_accessed = item.get("last_accessed")
            
            if last_accessed is None:
                # Never accessed = old
                old_items.append(item)
            else:
                # Check age
                days_since = (now - last_accessed).total_seconds() / 86400.0
                
                if days_since >= days_threshold:
                    old_items.append(item)
        
        # Create archive
        if old_items:
            archive = self.archive_manager.create_archive(old_items)
            
            if archive:
                archived_items = archive.items
                self.archive_manager.update_index(archive)
            else:
                archived_items = [item.get("path", "") for item in old_items]
        else:
            archived_items = []
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        
        return ConsolidationResult(
            deleted_items=[],
            archived_items=archived_items,
            merged_items=[],
            space_saved=0,
            time_taken=time_taken
        )
    
    def perform_consolidation(self, items: List[Dict[str, Any]]) -> ConsolidationResult:
        """
        Perform full consolidation: duplicates, similar items, old items.
        
        Args:
            items: List of memory items
        
        Returns:
            ConsolidationResult with all consolidation results
        """
        start_time = datetime.now()
        
        all_deleted = []
        all_archived = []
        total_space_saved = 0
        
        # 1. Find and consolidate duplicates
        duplicate_groups = self.find_duplicates(items)
        duplicate_result = self.consolidate_duplicates(duplicate_groups)
        
        all_deleted.extend(duplicate_result.deleted_items)
        all_archived.extend(duplicate_result.archived_items)
        total_space_saved += duplicate_result.space_saved
        
        # 2. Find and consolidate similar items
        similar_groups = self.find_similar_items(items, threshold=0.8)
        similar_result = self.consolidate_similar(similar_groups)
        
        all_archived.extend(similar_result.archived_items)
        total_space_saved += similar_result.space_saved
        
        # 3. Archive old items
        old_items_result = self.archive_old_items(items, days_threshold=90)
        
        all_archived.extend(old_items_result.archived_items)
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        
        return ConsolidationResult(
            deleted_items=all_deleted,
            archived_items=all_archived,
            merged_items=[],
            space_saved=total_space_saved,
            time_taken=time_taken
        )
