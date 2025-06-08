from typing import Dict, List

from pattern_searcher import PatternSearcher, SearchMatch


class BoyerMooreSearcher(PatternSearcher):
    """Boyer-Moore algorithm with unified multi-pattern interface."""

    def __init__(self, use_complex: bool = True):
        """
        Args:
            use_complex (bool): True if using good suffix heuristic.
        """

        self.use_complex = use_complex

    def _build_bad_character_table(self, pattern: str) -> Dict[str, int]:
        """
        Build the bad character table for Boyer-Moore algorithm.

        Args:
            pattern (str): The pattern for which to build the bad character table

        Returns:
            Dict[str, int]: Dictionary mapping characters to their rightmost position in pattern
        """
        bad_char: Dict[str, int] = {}
        for i in range(len(pattern)):
            bad_char[pattern[i]] = i
        return bad_char

    def _build_good_suffix_table(self, pattern: str) -> List[int]:
        """
        Build the good suffix table for Boyer-Moore algorithm.

        Args:
            pattern (str): The pattern for which to build the good suffix table

        Returns:
            List[int]: Array where good_suffix[i] contains the shift value for position i
        """
        pattern_length: int = len(pattern)
        good_suffix: List[int] = [0] * (pattern_length + 1)
        border: List[int] = [0] * (pattern_length + 1)

        # Compute border array (similar to KMP failure function)
        pattern_index: int = pattern_length
        suffix_index: int = pattern_length + 1
        border[pattern_index] = suffix_index

        while pattern_index > 0:
            while (
                suffix_index <= pattern_length
                and pattern[pattern_index - 1] != pattern[suffix_index - 1]
            ):
                if good_suffix[suffix_index] == 0:
                    good_suffix[suffix_index] = suffix_index - pattern_index
                suffix_index = border[suffix_index]
            pattern_index -= 1
            suffix_index -= 1
            border[pattern_index] = suffix_index

        # Fill remaining entries
        suffix_index = border[0]
        for pattern_index in range(pattern_length + 1):
            if good_suffix[pattern_index] == 0:
                good_suffix[pattern_index] = suffix_index
            if pattern_index == suffix_index:
                suffix_index = border[suffix_index]

        return good_suffix

    def _boyer_moore_simple(self, text: str, pattern: str) -> List[int]:
        """
        Boyer-Moore algorithm using only bad character heuristic.

        Args:
            text (str): The text to search in
            pattern (str): The pattern to search for

        Returns:
            List[int]: List of starting indices where pattern is found in text
        """
        text_length: int = len(text)
        pattern_length: int = len(pattern)
        matches: List[int] = []

        if not pattern or not text:
            return matches

        if pattern_length > text_length:
            return matches

        # Build bad character table
        bad_char: Dict[str, int] = self._build_bad_character_table(pattern)

        shift: int = 0
        while shift <= text_length - pattern_length:
            pattern_index: int = pattern_length - 1

            # Match pattern from right to left
            while (
                pattern_index >= 0
                and pattern[pattern_index] == text[shift + pattern_index]
            ):
                pattern_index -= 1

            if pattern_index < 0:
                # Pattern found
                matches.append(shift)
                # Shift to next possible position
                shift += (
                    pattern_length - bad_char.get(text[shift + pattern_length], -1)
                    if shift + pattern_length < text_length
                    else 1
                )
            else:
                # Mismatch occurred, use bad character heuristic
                bad_char_shift = pattern_index - bad_char.get(
                    text[shift + pattern_index], -1
                )
                shift += max(1, bad_char_shift)

        return matches

    def _boyer_moore_complex(self, text: str, pattern: str) -> List[int]:
        """
        Boyer-Moore algorithm using both bad character and good suffix heuristics.

        Args:
            text (str): The text to search in
            pattern (str): The pattern to search for

        Returns:
            List[int]: List of starting indices where pattern is found in text
        """
        text_length: int = len(text)
        pattern_length: int = len(pattern)
        matches: List[int] = []

        if not pattern or not text:
            return matches

        if pattern_length > text_length:
            return matches

        # Build bad character and good suffix tables
        bad_char: Dict[str, int] = self._build_bad_character_table(pattern)
        good_suffix: List[int] = self._build_good_suffix_table(pattern)

        shift: int = 0
        while shift <= text_length - pattern_length:
            pattern_index: int = pattern_length - 1

            # Match pattern from right to left
            while (
                pattern_index >= 0
                and pattern[pattern_index] == text[shift + pattern_index]
            ):
                pattern_index -= 1

            if pattern_index < 0:
                # Pattern found
                matches.append(shift)
                shift += good_suffix[0]
            else:
                # Mismatch occurred, use both heuristics
                bad_char_shift = pattern_index - bad_char.get(
                    text[shift + pattern_index], -1
                )
                good_suffix_shift = good_suffix[pattern_index + 1]
                shift += max(bad_char_shift, good_suffix_shift)

        return matches

    def search_multiple(self, text: str, patterns: List[str]) -> List[SearchMatch]:
        """Search for multiple patterns using Boyer-Moore algorithm."""
        if not text or not patterns:
            return []

        # Filter out empty patterns
        valid_patterns = [p for p in patterns if p and len(p.strip()) > 0]
        if not valid_patterns:
            return []

        matches: List[SearchMatch] = []
        search_func = (
            self._boyer_moore_complex if self.use_complex else self._boyer_moore_simple
        )

        # Use Boyer-Moore for each pattern
        for pattern in valid_patterns:
            positions = search_func(text, pattern)
            for start_pos in positions:
                end_pos = start_pos + len(pattern) - 1
                match = SearchMatch(
                    pattern=pattern,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    similarity=1.0,
                )
                matches.append(match)

        # Sort by position, then by pattern for deterministic results
        matches.sort(key=lambda x: (x.start_pos, x.pattern))
        return matches

    @property
    def algorithm_name(self) -> str:
        return "Boyer-Moore Complex" if self.use_complex else "Boyer-Moore Simple"

    @property
    def is_exact_match(self) -> bool:
        return True
