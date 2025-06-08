from collections import deque
from typing import Dict, List, Optional

from algorithms.pattern_searcher import PatternSearcher, SearchMatch


class TrieNode:
    """Node class for the Trie structure used in Aho-Corasick algorithm."""

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}  # Dictionary to store child nodes
        self.failure: Optional["TrieNode"] = None  # Failure link for Aho-Corasick
        self.output: List[str] = []  # List of patterns that end at this node
        self.is_end: bool = False  # Flag to mark end of a pattern


class AhoCorasick:
    """
    Aho-Corasick algorithm implementation for multiple pattern matching.

    The algorithm works in three phases:
    1. Build a trie of all patterns
    2. Construct failure links (similar to KMP failure function)
    3. Search for all patterns in the text using the automaton
    """

    def __init__(self) -> None:
        self.root: TrieNode = TrieNode()
        self.patterns: List[str] = []  # Store original patterns for reference
        self._failure_links_built: bool = False

    def add_pattern(self, pattern: str) -> None:
        """
        Add a pattern to the trie.

        Args:
            pattern (str): The pattern to add
        """
        if not pattern:
            return

        self.patterns.append(pattern)
        node: TrieNode = self.root

        # Build trie by adding each character
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        # Mark end of pattern and store the pattern
        node.is_end = True
        node.output.append(pattern)

        self._failure_links_built = False

    def _build_failure_links(self) -> None:
        """
        Build failure links for the Aho-Corasick automaton.

        This creates failure links that allow efficient backtracking
        when a mismatch occurs during pattern matching.
        """
        if self._failure_links_built:
            return

        queue: deque[TrieNode] = deque()

        # Initialize failure links for root's children
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)

        # BFS to build failure links
        while queue:
            current: TrieNode = queue.popleft()

            for char, child in current.children.items():
                queue.append(child)

                # Find failure link for this child
                failure_node: Optional[TrieNode] = current.failure

                # Follow failure links until we find a match or reach root
                while failure_node is not None and char not in failure_node.children:
                    failure_node = failure_node.failure

                if failure_node is not None:
                    child.failure = failure_node.children[char]
                else:
                    child.failure = self.root

                # Copy output from failure node (for overlapping patterns)
                if child.failure is not None:
                    child.output.extend(child.failure.output)

        self._failure_links_built = True

    def search(self, text: str) -> List[tuple[int, int, str]]:
        """
        Search for all patterns in the given text.

        Args:
            text (str): The text to search in

        Returns:
            List[tuple[int, int, str]]: List of tuples (start_index, end_index, pattern)
                                       representing matches found in the text
        """
        if not text or not self.patterns:
            return []

        # Build the automaton if not already built
        self._build_failure_links()

        matches: List[tuple[int, int, str]] = []
        current_node: Optional[TrieNode] = self.root

        for i, char in enumerate(text):
            # Follow failure links until we find a match or reach root
            while current_node is not None and char not in current_node.children:
                current_node = current_node.failure

            if current_node is None:
                current_node = self.root
                continue

            # Move to next state
            current_node = current_node.children[char]

            # Check for pattern matches at current position
            for pattern in current_node.output:
                start_index: int = i - len(pattern) + 1
                end_index: int = i
                matches.append((start_index, end_index, pattern))

        return matches


class AhoCorasickSearcher(PatternSearcher):
    """Aho-Corasick algorithm with caching for repeated pattern sets."""

    def __init__(self):
        self._ac_instance: Optional[AhoCorasick] = None
        self._cached_patterns: List[str] = []

    def search_multiple(self, text: str, patterns: List[str]) -> List[SearchMatch]:
        """Search for multiple patterns using Aho-Corasick algorithm."""
        if not text or not patterns:
            return []

        # Filter out empty patterns
        valid_patterns = [p for p in patterns if p and len(p.strip()) > 0]
        if not valid_patterns:
            return []

        # Check if we need to rebuild the automaton
        if self._ac_instance is None or set(self._cached_patterns) != set(
            valid_patterns
        ):
            self._build_automaton(valid_patterns)

        # Perform search
        raw_matches = self._ac_instance.search(text)  # type: ignore
        matches: List[SearchMatch] = []

        for start_pos, end_pos, pattern in raw_matches:
            match = SearchMatch(
                pattern=pattern, start_pos=start_pos, end_pos=end_pos, similarity=1.0
            )
            matches.append(match)

        # Sort by position, then by pattern for deterministic results
        matches.sort(key=lambda x: (x.start_pos, x.pattern))
        return matches

    def _build_automaton(self, patterns: List[str]) -> None:
        """Build or rebuild the Aho-Corasick automaton."""
        self._ac_instance = AhoCorasick()
        for pattern in patterns:
            self._ac_instance.add_pattern(pattern)
        self._cached_patterns = patterns.copy()

    def clear_cache(self) -> None:
        """Clear the cached automaton."""
        self._ac_instance = None
        self._cached_patterns = []

    @property
    def algorithm_name(self) -> str:
        return "Aho-Corasick"

    @property
    def is_exact_match(self) -> bool:
        return True
