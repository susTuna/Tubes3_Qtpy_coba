from collections import deque, defaultdict
from typing import Optional

class TrieNode:
    """Node class for the Trie structure used in Aho-Corasick algorithm."""
    def __init__(self) -> None:
        self.children: dict[str, 'TrieNode'] = {}  # Dictionary to store child nodes
        self.failure: Optional['TrieNode'] = None  # Failure link for Aho-Corasick
        self.output: list[str] = []     # List of patterns that end at this node
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
        self.patterns: list[str] = []  # Store original patterns for reference
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

    def build_failure_links(self) -> None:
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
    
    def search(self, text: str) -> list[tuple[int, int, str]]:
        """
        Search for all patterns in the given text.

        Args:
            text (str): The text to search in

        Returns:
            list[tuple[int, int, str]]: List of tuples (start_index, end_index, pattern)
                                       representing matches found in the text
        """
        if not text or not self.patterns:
            return []

        # Build the automaton if not already built
        self.build_failure_links()

        matches: list[tuple[int, int, str]] = []
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

    def search_all_positions(self, text: str) -> dict[str, list[tuple[int, int]]]:
        """
        Search for all patterns and return detailed position information.

        Args:
            text (str): The text to search in

        Returns:
            dict[str, list[tuple[int, int]]]: Dictionary with pattern as key 
                                              and list of (start, end) positions as value
        """
        matches: list[tuple[int, int, str]] = self.search(text)
        result: dict[str, list[tuple[int, int]]] = defaultdict(list)

        for start, end, pattern in matches:
            result[pattern].append((start, end))

        return dict(result)

    def contains_any(self, text: str) -> bool:
        """
        Check if text contains any of the patterns.

        Args:
            text (str): The text to check

        Returns:
            bool: True if any pattern is found, False otherwise
        """
        return len(self.search(text)) > 0

    def find_first_match(self, text: str) -> Optional[tuple[int, int, str]]:
        """
        Find the first occurrence of any pattern in the text.

        Args:
            text (str): The text to search in

        Returns:
            Optional[Tuple[int, int, str]]: (start_index, end_index, pattern) of first match,
                                          or None if no match found
        """
        if not text or not self.patterns:
            return None

        self.build_failure_links()
        current_node: Optional[TrieNode] = self.root

        for i, char in enumerate(text):
            while current_node is not None and char not in current_node.children:
                current_node = current_node.failure

            if current_node is None:
                current_node = self.root
                continue

            current_node = current_node.children[char]

            if current_node.output:
                pattern: str = current_node.output[0]
                start_index: int = i - len(pattern) + 1
                return (start_index, i, pattern)

        return None

    def get_patterns(self) -> list[str]:
        """
        Get all valid patterns (excluding empty ones).
    
        Returns:
            list[str]: List of valid patterns
        """
        return [p for p in self.patterns if p and len(p) > 0]

    def get_pattern_count(self) -> int:
        """
        Get the number of valid patterns.

        Returns:
            int: Number of valid patterns
        """
        return len(self.get_patterns())

    def clear(self) -> None:
        """
        Clear all patterns and reset the automaton.
        """
        self.root = TrieNode()
        self.patterns = []
        self._failure_links_built = False