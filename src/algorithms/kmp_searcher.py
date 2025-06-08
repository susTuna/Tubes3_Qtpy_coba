from typing import List

from pattern_searcher import PatternSearcher, SearchMatch


class KMPSearcher(PatternSearcher):
    """KMP algorithm with unified multi-pattern interface."""

    def _generate_lps_list(self, pattern: str) -> List[int]:
        """
        Generate the Longest Proper Prefix which is also Suffix (LPS) array.

        This array is used by the KMP algorithm to determine how much to skip
        when a mismatch occurs.

        Args:
            pattern (str): The pattern for which to generate the LPS array

        Returns:
            List[int]: LPS array where lps[i] contains the length of the longest
                       proper prefix of pattern[0..i] which is also a suffix of
                       pattern[0..i]
        """
        lps: List[int] = [0] * len(pattern)
        length: int = 0
        pointer: int = 1  # lsp[0] is always 0, start from index 1

        while pointer < len(pattern):
            if pattern[pointer] == pattern[length]:
                length += 1
                lps[pointer] = length
                pointer += 1
            else:
                if length == 0:
                    lps[pointer] = 0
                    pointer += 1
                else:
                    length = lps[length - 1]

        return lps

    def _kmp_search(self, text: str, pattern: str) -> List[int]:
        """
        Knuth-Morris-Pratt string searching algorithm.

        Args:
            text (str): The text to search in
            pattern (str): The pattern to search for

        Returns:
            List[int]: List of starting indices where pattern is found in text
        """
        matches: List[int] = []
        lps: List[int] = self._generate_lps_list(pattern)
        text_length: int = len(text)
        pattern_length: int = len(pattern)

        # Check for impossible case
        if not pattern or not text:
            return matches
        if pattern_length > text_length:
            return matches

        text_index: int = 0
        pattern_index: int = 0

        while text_index < text_length:
            if text[text_index] == pattern[pattern_index]:
                text_index += 1
                pattern_index += 1

                if pattern_index == pattern_length:
                    matches.append(text_index - pattern_index)
                    pattern_index = lps[pattern_index - 1]
            else:
                if pattern_index != 0:
                    pattern_index = lps[pattern_index - 1]
                else:
                    text_index += 1

        return matches

    def search_multiple(self, text: str, patterns: List[str]) -> List[SearchMatch]:
        """Search for multiple patterns using KMP algorithm."""

        if not text or not patterns:
            return []

        valid_patterns = [p for p in patterns if p and len(p.strip()) > 0]
        if not valid_patterns:
            return []

        matches: List[SearchMatch] = []

        for pattern in valid_patterns:
            positions: List[int] = self._kmp_search(text, pattern)
            for start_pos in positions:
                end_pos: int = start_pos + len(pattern) - 1
                match: SearchMatch = SearchMatch(
                    pattern=pattern,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    similarity=1.0,
                )
                matches.append(match)

        matches.sort(key=lambda x: (x.start_pos, x.pattern))

        return matches

    @property
    def algorithm_name(self) -> str:
        return "KMP"

    @property
    def is_exact_match(self) -> bool:
        return True
