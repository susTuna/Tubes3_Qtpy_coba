from collections import deque, defaultdict

class TrieNode:
    def __init__(self):
        self.children = {}  # Dictionary to store child nodes
        self.failure = None  # Failure link for Aho-Corasick
        self.output = []     # List of patterns that end at this node
        self.is_end = False  # Flag to mark end of a pattern

class AhoCorasick:
    def __init__(self):
        self.root = TrieNode()
        self.patterns = []  # Store original patterns for reference

    def add_pattern(self, pattern):
        if not pattern:
            return

        self.patterns.append(pattern)
        node = self.root

        # Build trie by adding each character
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        # Mark end of pattern and store the pattern
        node.is_end = True
        node.output.append(pattern)

    def build_failure_links(self):
        queue = deque()

        # Initialize failure links for root's children
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)

        # BFS to build failure links
        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                queue.append(child)

                # Find failure link for this child
                failure_node = current.failure

                # Follow failure links until we find a match or reach root
                while failure_node is not None and char not in failure_node.children:
                    failure_node = failure_node.failure

                if failure_node is not None:
                    child.failure = failure_node.children[char]
                else:
                    child.failure = self.root

                # Copy output from failure node (for overlapping patterns)
                child.output.extend(child.failure.output)
    
    def search(self, text):
        if not text or not self.patterns:
            return []

        # Build the automaton if not already built
        self.build_failure_links()

        matches = []
        current_node = self.root

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
                start_index = i - len(pattern) + 1
                end_index = i
                matches.append((start_index, end_index, pattern))

        return matches

    def search_all_positions(self, text):
        matches = self.search(text)
        result = defaultdict(list)

        for start, end, pattern in matches:
            result[pattern].append((start, end))

        return dict(result)

    def contains_any(self, text):
        return len(self.search(text)) > 0

    def find_first_match(self, text):
        if not text or not self.patterns:
            return None

        self.build_failure_links()
        current_node = self.root

        for i, char in enumerate(text):
            while current_node is not None and char not in current_node.children:
                current_node = current_node.failure

            if current_node is None:
                current_node = self.root
                continue

            current_node = current_node.children[char]

            if current_node.output:
                pattern = current_node.output[0]
                start_index = i - len(pattern) + 1
                return (start_index, i, pattern)

        return None

# Convenience functions for easy usage
def _build_automaton(patterns):
    ac = AhoCorasick()
    for pattern in patterns:
        ac.add_pattern(pattern)
    return ac

def _search_multiple_patterns(text, patterns):
    ac = _build_automaton(patterns)
    return ac.search(text)