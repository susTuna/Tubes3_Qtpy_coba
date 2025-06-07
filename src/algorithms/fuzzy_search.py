def levenshtein_distance(str1: str, str2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string
    into another.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        int: The Levenshtein distance between the two strings
    """
    if not str1:
        return len(str2)
    if not str2:
        return len(str1)

    # Ensure str1 is the shorter string for space optimization
    if len(str1) > len(str2):
        str1, str2 = str2, str1

    len1: int = len(str1)
    len2: int = len(str2)

    prev_row: list[int] = list(range(len1 + 1))
    curr_row: list[int] = [0] * (len1 + 1)

    for j in range(1, len2 + 1):
        curr_row[0] = j

        for i in range(1, len1 + 1):
            if str1[i - 1] == str2[j - 1]:
                curr_row[i] = prev_row[i - 1]
            else:
                curr_row[i] = min(
                    prev_row[i] + 1,      # Deletion
                    curr_row[i - 1] + 1,  # Insertion
                    prev_row[i - 1] + 1   # Substitution
                )

        prev_row, curr_row = curr_row, prev_row

    return prev_row[len1]

def similarity_ratio(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings (0.0 to 1.0).

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        float: Similarity ratio (1.0 = identical, 0.0 = completely different)
    """
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0

    max_len: int = max(len(str1), len(str2))
    distance: int = levenshtein_distance(str1, str2)

    return 1.0 - (distance / max_len)

def fuzzy_search_text(query: str, text: str, min_similarity: float, max_results: int) -> list[tuple[int, int, str, float]]:
    """
    Fuzzy search in text using similarity ratio threshold.

    Args:
        query (str): The search query
        text (str): The text to search in
        min_similarity (float): Minimum similarity ratio (0.0 to 1.0)
        max_results (int): Maximum number of results to return

    Returns:
        List[Tuple[int, int, str, float]]: List of tuples (start_index, end_index, substring, similarity)
                                           sorted by similarity (highest to lowest)
    """
    if not query or not text:
        return []

    query_len: int = len(query)
    text_len: int = len(text)
    matches: list[tuple[int, int, str, float]] = []

    # Calculate reasonable window size based on similarity threshold
    # Lower similarity means need to check longer substrings
    max_length_ratio: float = 1.0 / min_similarity if min_similarity > 0 else 3.0
    max_window: int = min(int(query_len * max_length_ratio), text_len)

    # Also set a minimum window size
    min_window: int = max(1, int(query_len * min_similarity))

    for start in range(text_len):
        for length in range(min_window, min(max_window + 1, text_len - start + 1)):
            end: int = start + length
            substring: str = text[start:end]

            similarity: float = similarity_ratio(query, substring)

            if similarity >= min_similarity:
                matches.append((start, end - 1, substring, similarity))

    # Sort by similarity (highest to lowest), then by start position for ties
    matches.sort(key=lambda x: (-x[3], x[0]))

    # Return only the requested number of results
    return matches[:max_results]

def fuzzy_search_candidates(query: str, candidates: list[str], min_similarity: float, max_results: int) -> list[tuple[str, float, int]]:
    """
    Fuzzy search in a list of candidate strings using similarity ratio threshold.

    Args:
        query (str): The search query
        candidates (List[str]): List of candidate strings to search through
        min_similarity (float): Minimum similarity ratio (0.0 to 1.0)
        max_results (int): Maximum number of results to return

    Returns:
        List[Tuple[str, float, int]]: List of tuples (candidate, similarity, original_index)
                                      sorted by similarity (highest to lowest)
    """
    if not query or not candidates:
        return []

    matches: list[tuple[str, float, int]] = []

    for i, candidate in enumerate(candidates):
        if not candidate:  # Skip empty strings
            continue

        similarity: float = similarity_ratio(query, candidate)

        if similarity >= min_similarity:
            matches.append((candidate, similarity, i))

    # Sort by similarity (highest to lowest), then by original index for ties
    matches.sort(key=lambda x: (-x[1], x[2]))

    # Return only the requested number of results
    return matches[:max_results]