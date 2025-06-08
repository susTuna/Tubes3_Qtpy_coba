from typing import List, Tuple

from pattern_searcher import PatternSearcher, SearchMatch


class FuzzySearcher(PatternSearcher):
    """Fuzzy search algorithm with configurable similarity threshold."""

    def __init__(self, min_similarity: float = 0.6, max_results_per_pattern: int = 100):
        self.min_similarity = min_similarity
        self.max_results_per_pattern = max_results_per_pattern

    def _levenshtein_distance(self, str1: str, str2: str) -> int:
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

        prev_row: List[int] = list(range(len1 + 1))
        curr_row: List[int] = [0] * (len1 + 1)

        for j in range(1, len2 + 1):
            curr_row[0] = j

            for i in range(1, len1 + 1):
                if str1[i - 1] == str2[j - 1]:
                    curr_row[i] = prev_row[i - 1]
                else:
                    curr_row[i] = min(
                        prev_row[i] + 1,  # Deletion
                        curr_row[i - 1] + 1,  # Insertion
                        prev_row[i - 1] + 1,  # Substitution
                    )

            prev_row, curr_row = curr_row, prev_row

        return prev_row[len1]

    def _similarity_ratio(self, str1: str, str2: str) -> float:
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
        distance: int = self._levenshtein_distance(str1, str2)

        return 1.0 - (distance / max_len)

    def _fuzzy_search_text(
        self, query: str, text: str, min_similarity: float, max_results: int
    ) -> List[Tuple[int, int, str, float]]:
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
        matches: List[Tuple[int, int, str, float]] = []

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

                similarity: float = self._similarity_ratio(query, substring)

                if similarity >= min_similarity:
                    matches.append((start, end - 1, substring, similarity))

        # Sort by similarity (highest to lowest), then by start position for ties
        matches.sort(key=lambda x: (-x[3], x[0]))

        # Return only the requested number of results
        return matches[:max_results]

    def search_multiple(self, text: str, patterns: List[str]) -> List[SearchMatch]:
        """Search for multiple patterns using fuzzy matching."""
        if not text or not patterns:
            return []

        # Filter out empty patterns
        valid_patterns = [p for p in patterns if p and len(p.strip()) > 0]
        if not valid_patterns:
            return []

        matches: List[SearchMatch] = []

        # Use fuzzy search for each pattern
        for pattern in valid_patterns:
            fuzzy_matches = self._fuzzy_search_text(
                query=pattern,
                text=text,
                min_similarity=self.min_similarity,
                max_results=self.max_results_per_pattern,
            )

            for start_pos, end_pos, snippet, similarity in fuzzy_matches:
                match = SearchMatch(
                    pattern=pattern,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    similarity=similarity,
                )
                matches.append(match)

        # Sort by similarity (highest first), then by position
        matches.sort(key=lambda x: (-x.similarity, x.start_pos))
        return matches

    def set_similarity_threshold(self, min_similarity: float) -> None:
        """Update the minimum similarity threshold."""
        if not 0.0 <= min_similarity <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        self.min_similarity = min_similarity

    @property
    def algorithm_name(self) -> str:
        return f"Fuzzy Search (min_sim={self.min_similarity:.2f})"

    @property
    def is_exact_match(self) -> bool:
        return False
