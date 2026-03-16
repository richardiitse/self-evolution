"""
Similarity Utils - Common similarity calculation functions.

Extracted from memory_consolidation.py and cross_skill_transfer.py
to eliminate code duplication.

Functions:
- calculate_name_similarity: Name similarity using edit distance
- calculate_content_similarity: Content similarity using word frequencies
- calculate_key_overlap_similarity: Set key overlap similarity
- calculate_cosine_similarity: Cosine similarity of vectors
"""

from typing import Dict, List, Set, Tuple, Any


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate name similarity using edit distance (Levenshtein distance).

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

    # Simple edit distance (Levenshtein)
    len1, len2 = len(norm1), len(norm2)
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        matrix[i][0] = i

    for j in range(1, len2 + 1):
        matrix[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if norm1[i - 1] == norm2[j - 1]:
                cost = matrix[i - 1][j - 1]
            else:
                cost = min(
                    matrix[i - 1][j] + 1,      # deletion
                    matrix[i][j - 1] + 1,      # insertion
                    matrix[i - 1][j - 1] + 1   # substitution
                )
            matrix[i][j] = cost

    # Calculate similarity from edit distance
    max_len = max(len1, len2)
    if max_len == 0:
        return 1.0

    edit_distance = matrix[len1][len2]
    similarity = 1.0 - (edit_distance / max_len)

    return max(0.0, similarity)


def calculate_key_overlap_similarity(
    keys1: Set[str],
    keys2: Set[str]
) -> float:
    """
    Calculate similarity based on key overlap between two sets.

    Args:
        keys1: First set of keys
        keys2: Second set of keys

    Returns:
        Similarity score (0.0 - 1.0)
    """
    if not keys1 or not keys2:
        return 0.0

    # Count overlapping keys
    overlap = len(keys1.intersection(keys2))

    # Calculate similarity using Jaccard index
    total_keys = len(keys1.union(keys2))
    if total_keys == 0:
        return 0.0

    return overlap / total_keys


def calculate_content_similarity(content1: str, content2: str) -> float:
    """
    Calculate content similarity using word frequencies (cosine similarity).

    Args:
        content1: First content
        content2: Second content

    Returns:
        Similarity score (0.0 - 1.0)
    """
    # Tokenize into words
    words1 = content1.lower().split()
    words2 = content2.lower().split()

    if not words1 or not words2:
        return 0.0

    # Create word frequency maps
    freq1: Dict[str, int] = {}
    freq2: Dict[str, int] = {}

    for word in words1:
        freq1[word] = freq1.get(word, 0) + 1

    for word in words2:
        freq2[word] = freq2.get(word, 0) + 1

    # Calculate cosine similarity
    return calculate_cosine_similarity(freq1, freq2)


def calculate_cosine_similarity(
    vec1: Dict[str, float],
    vec2: Dict[str, float]
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector (dict mapping terms to weights)
        vec2: Second vector (dict mapping terms to weights)

    Returns:
        Cosine similarity (0.0 - 1.0)
    """
    # Get all unique terms
    all_terms = set(vec1.keys()).union(set(vec2.keys()))

    if not all_terms:
        return 0.0

    # Calculate dot product and magnitudes
    dot_product = 0.0
    norm1_sq = 0.0
    norm2_sq = 0.0

    for term in all_terms:
        v1 = vec1.get(term, 0.0)
        v2 = vec2.get(term, 0.0)

        dot_product += v1 * v2
        norm1_sq += v1 ** 2
        norm2_sq += v2 ** 2

    # Avoid division by zero
    if norm1_sq == 0 or norm2_sq == 0:
        return 0.0

    similarity = dot_product / ((norm1_sq ** 0.5) * (norm2_sq ** 0.5))

    return max(0.0, min(1.0, similarity))


def calculate_string_similarity(str1: str, str2: str) -> float:
    """
    Calculate string similarity based on common characters.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity score (0.0 - 1.0)
    """
    if not str1 or not str2:
        return 0.0

    if str1 == str2:
        return 1.0

    # Calculate character overlap
    common_chars = set(str1).intersection(set(str2))
    total_chars = len(set(str1).union(set(str2)))

    if total_chars == 0:
        return 0.0

    return len(common_chars) / total_chars


def calculate_metadata_similarity(
    metadata1: Dict[str, Any],
    metadata2: Dict[str, Any]
) -> float:
    """
    Calculate metadata similarity based on matching keys and values.

    Args:
        metadata1: First metadata dictionary
        metadata2: Second metadata dictionary

    Returns:
        Similarity score (0.0 - 1.0)
    """
    if not metadata1 or not metadata2:
        return 0.0

    # Count matching metadata keys
    matching_keys = 0
    for key in metadata1.keys():
        if key in metadata2 and metadata1[key] == metadata2[key]:
            matching_keys += 1

    if not matching_keys:
        return 0.0

    total_keys = len(metadata1.keys())
    return matching_keys / total_keys
