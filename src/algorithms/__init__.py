"""
String Matching Algorithms Package
==========================================

This package provides a unified interface for various string matching algorithms with automatic
fallback capabilities. All algorithms implement the same PatternSearcher interface for consistency.

Quick Start
-----------
For most use cases, use the high-level search functions:

    >>> from algorithms import search_text, fuzzy_search
    >>>
    >>> # Simple search with automatic exact->fuzzy fallback
    >>> matches = search_text("Hello Python world", ["Python", "Java"])
    >>> print(f"Found {len(matches)} matches")
    >>>
    >>> # Fuzzy search only
    >>> fuzzy_matches = fuzzy_search("Hello Pythn world", ["Python"], min_similarity=0.8)

Algorithm Types
---------------
The package includes two categories of algorithms:

**Exact Match Algorithms** (exact substring matching):
- KMP (Knuth-Morris-Pratt): Linear time, good for single patterns
- Boyer-Moore Simple: Uses bad character heuristic only
- Boyer-Moore Complex: Uses both bad character and good suffix heuristics
- Aho-Corasick: Optimal for multiple pattern matching

**Fuzzy Search Algorithm** (approximate matching):
- Edit Distance Based: Finds similar patterns using Levenshtein distance

Core Classes and Functions
--------------------------

SearchEngine
~~~~~~~~~~~~~~~~~~~
The main search engine that handles algorithm selection and fallback logic.

Example usage:
    >>> from algorithms import SearchEngine, SearchConfig, AlgorithmType
    >>>
    >>> # Create engine with custom configuration
    >>> config = SearchConfig(
    ...     case_sensitive=False,
    ...     max_results=50,
    ...     exact_algorithm=AlgorithmType.AHO_CORASICK,
    ...     fuzzy_min_similarity=0.7,
    ...     use_fuzzy_fallback=True
    ... )
    >>> engine = SearchEngine(config)
    >>>
    >>> # Search with automatic fallback
    >>> matches, stats = engine.search("Sample text content", ["pattern1", "pattern2"])
    >>> print(f"Strategy used: {stats.strategy_used}")
    >>> print(f"Found {stats.exact_matches_count} exact + {stats.fuzzy_matches_count} fuzzy matches")

SearchMatch Data Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~
All search results are returned as SearchMatch objects with consistent fields:

    >>> match = matches[0]  # Get first match
    >>> print(f"Pattern: '{match.pattern}'")
    >>> print(f"Position: {match.start_pos}-{match.end_pos}")
    >>> print(f"Length: {match.length}")
    >>> print(f"Similarity: {match.similarity}")  # 1.0 for exact, <1.0 for fuzzy

Individual Algorithm Usage
--------------------------

If you need to use specific algorithms directly:

    >>> from algorithms import create_searcher
    >>>
    >>> # Create specific algorithm instances
    >>> kmp_searcher = create_searcher('kmp')
    >>> ac_searcher = create_searcher('aho_corasick')
    >>> fuzzy_searcher = create_searcher('fuzzy')
    >>>
    >>> # All use the same interface
    >>> text = "Sample text for searching"
    >>> patterns = ["text", "sample", "search"]
    >>>
    >>> kmp_results = kmp_searcher.search_multiple(text, patterns)
    >>> ac_results = ac_searcher.search_multiple(text, patterns)

Configuration Options
---------------------

SearchConfig allows fine-tuning of search behavior:

    >>> config = SearchConfig(
    ...     case_sensitive=True,           # Match case exactly
    ...     max_results=100,               # Limit number of results
    ...     exact_algorithm=AlgorithmType.KMP,  # Choose exact algorithm
    ...     fuzzy_min_similarity=0.8,     # Minimum similarity for fuzzy matches
    ...     use_fuzzy_fallback=True       # Enable automatic fallback to fuzzy search
    ... )

Available exact algorithms:
- AlgorithmType.KMP
- AlgorithmType.BOYER_MOORE_SIMPLE
- AlgorithmType.BOYER_MOORE_COMPLEX
- AlgorithmType.AHO_CORASICK

Performance Guidelines
----------------------

**Choose algorithms based on your use case:**

- **Single pattern, small text**: KMP or Boyer-Moore
- **Single pattern, large text**: Boyer-Moore Complex
- **Multiple patterns**: Aho-Corasick (optimal choice)
- **Approximate matching needed**: Fuzzy Search
- **Mixed requirements**: SearchEngine with fallback

**Performance comparison** (run benchmark to get actual numbers):
    >>> from algorithms import SearchEngine
    >>> engine = SearchEngine()
    >>> timing_results = engine.benchmark_algorithms(your_text, your_patterns)
    >>> for algo, time_taken in timing_results.items():
    ...     print(f"{algo}: {time_taken:.4f} seconds")

Advanced Usage Examples
-----------------------

**Case-insensitive search with specific algorithm:**
    >>> config = SearchConfig(case_sensitive=False, exact_algorithm=AlgorithmType.KMP)
    >>> engine = SearchEngine(config)
    >>> matches, stats = engine.search("Hello WORLD", ["world"])

**Exact matching only (no fuzzy fallback):**
    >>> matches, stats = engine.search_exact_only("text", ["pattern"], AlgorithmType.AHO_CORASICK)

**Fuzzy matching only:**
    >>> matches, stats = engine.search_fuzzy_only("text", ["patern"], min_similarity=0.6)

**Multiple search strategies:**
    >>> # Try exact first, then fuzzy if no results
    >>> exact_matches, _ = engine.search_exact_only(text, patterns)
    >>> if not exact_matches:
    ...     fuzzy_matches, _ = engine.search_fuzzy_only(text, patterns, min_similarity=0.7)

**Working with results:**
    >>> for match in matches:
    ...     print(f"Found '{match.pattern}' at position {match.start_pos}")
    ...     if match.similarity < 1.0:
    ...         print(f"  Similarity: {match.similarity:.2%}")

Error Handling
--------------

The package handles common errors gracefully:

    >>> # Empty patterns are filtered out automatically
    >>> matches = search_text("text", ["", "valid_pattern", ""])  # Only searches "valid_pattern"
    >>>
    >>> # Invalid algorithms raise ValueError
    >>> try:
    ...     searcher = create_searcher('invalid_algorithm')
    ... except ValueError as e:
    ...     print(f"Error: {e}")

Integration with GUI
--------------------

The package is designed to work seamlessly with PyQt6 GUIs:

    >>> # In your GUI controller
    >>> from algorithms import SearchEngine, SearchConfig
    >>>
    >>> class SearchController:
    ...     def __init__(self):
    ...         self.engine = SearchEngine()
    ...
    ...     def perform_search(self, text, patterns, algorithm_name):
    ...         # Convert GUI selections to config
    ...         config = SearchConfig(
    ...             exact_algorithm=AlgorithmType(algorithm_name.lower()),
    ...             case_sensitive=self.gui.case_sensitive_checkbox.isChecked(),
    ...             max_results=self.gui.max_results_spinbox.value()
    ...         )
    ...
    ...         # Perform search
    ...         matches, stats = self.engine.search(text, patterns, config)
    ...
    ...         # Update GUI with results
    ...         self.gui.display_results(matches, stats)

Package Structure Reference
---------------------------

algorithms/
├── __init__.py              # This file - main documentation and exports
├── pattern_searcher.py      # Abstract base class PatternSearcher
├── search_engine.py         # SearchEngine implementation
├── kmp_searcher.py         # KMP algorithm implementation
├── boyer_moore.py          # Boyer-Moore algorithms
├── aho_corasick.py         # Aho-Corasick algorithm
└── fuzzy_searcher.py       # Fuzzy search implementation

Troubleshooting
---------------

**Common issues and solutions:**

1. **No matches found when expected:**
   - Check case sensitivity settings
   - Try fuzzy search with lower similarity threshold
   - Verify patterns don't have leading/trailing spaces

2. **Slow performance:**
   - Use Aho-Corasick for multiple patterns
   - Reduce max_results limit
   - Consider case-sensitive search if applicable

3. **Memory usage too high:**
   - Limit max_results
   - Process text in chunks for very large files
   - Clear engine cache: engine._exact_searchers[AlgorithmType.AHO_CORASICK].clear_cache()

Version Information
-------------------
Package version: 1.0.0
Compatible with Python 3.8+
Requires: typing, dataclasses, enum (all standard library)

For more detailed algorithm implementations, see individual module files.
"""

from aho_corasick import AhoCorasickSearcher
from boyer_moore import BoyerMooreSearcher
from fuzzy_searcher import FuzzySearcher

# Import individual searcher implementations
from kmp_searcher import KMPSearcher

# Import all public interfaces
from pattern_searcher import PatternSearcher, SearchMatch, SearchStrategy
from search_engine import (
    AlgorithmType,
    SearchConfig,
    SearchEngine,
    SearchStats,
)


# Factory function for creating searchers
def create_searcher(algorithm: str) -> PatternSearcher:
    """
    Factory function to create searcher instances.

    Args:
        algorithm (str): Name of the algorithm. Options:
            - 'kmp': Knuth-Morris-Pratt algorithm
            - 'boyer_moore_simple': Boyer-Moore with bad character heuristic only
            - 'boyer_moore_complex': Boyer-Moore with both heuristics
            - 'aho_corasick': Aho-Corasick multi-pattern algorithm
            - 'fuzzy': Fuzzy search with edit distance

    Returns:
        PatternSearcher: Configured searcher instance

    Raises:
        ValueError: If algorithm name is not recognized

    Examples:
        >>> kmp = create_searcher('kmp')
        >>> results = kmp.search_multiple("text", ["pattern"])

        >>> ac = create_searcher('aho_corasick')  # Best for multiple patterns
        >>> results = ac.search_multiple("text", ["pat1", "pat2", "pat3"])
    """
    searchers = {
        "kmp": lambda: KMPSearcher(),
        "boyer_moore_simple": lambda: BoyerMooreSearcher(use_complex=False),
        "boyer_moore_complex": lambda: BoyerMooreSearcher(use_complex=True),
        "aho_corasick": lambda: AhoCorasickSearcher(),
        "fuzzy": lambda: FuzzySearcher(),
    }

    algorithm_lower = algorithm.lower().replace("-", "_").replace(" ", "_")
    searcher_factory = searchers.get(algorithm_lower)

    if not searcher_factory:
        available = ", ".join(searchers.keys())
        raise ValueError(f"Unknown algorithm '{algorithm}'. Available: {available}")

    return searcher_factory()


# High-level convenience functions
def search_text(
    text: str,
    patterns: str | list[str],
    algorithm: str = "aho_corasick",
    case_sensitive: bool = True,
    use_fuzzy_fallback: bool = True,
    max_results: int = 100,
) -> list[SearchMatch]:
    """
    High-level search function with sensible defaults.

    This is the recommended function for most use cases. It automatically tries
    exact matching first, then falls back to fuzzy search if no matches are found.

    Args:
        text (str): Text to search in
        patterns (str | list[str]): Pattern(s) to search for
        algorithm (str): Exact matching algorithm to use. Options:
            - "kmp": Good for single patterns
            - "boyer_moore_simple": Fast for single patterns
            - "boyer_moore_complex": Fastest for single patterns
            - "aho_corasick": Best for multiple patterns (default)
        case_sensitive (bool): Whether search should be case sensitive
        use_fuzzy_fallback (bool): Whether to try fuzzy search if no exact matches
        max_results (int): Maximum number of results to return

    Returns:
        list[SearchMatch]: List of matches found, sorted by position

    Examples:
        >>> # Single pattern search
        >>> matches = search_text("Hello Python world", "Python")
        >>> print(matches[0].pattern)  # "Python"

        >>> # Multiple patterns (recommended: use default aho_corasick)
        >>> matches = search_text("Code in Python or Java", ["Python", "Java", "C++"])
        >>>
        >>> # Case insensitive search
        >>> matches = search_text("Hello WORLD", "world", case_sensitive=False)
        >>>
        >>> # Disable fuzzy fallback for exact matches only
        >>> matches = search_text("text", "pattern", use_fuzzy_fallback=False)
    """
    # Convert algorithm string to enum
    try:
        algo_enum = AlgorithmType(algorithm.lower())
    except ValueError:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. Use create_searcher() for more options."
        )

    # Create configuration
    config = SearchConfig(
        case_sensitive=case_sensitive,
        max_results=max_results,
        exact_algorithm=algo_enum,
        use_fuzzy_fallback=use_fuzzy_fallback,
    )

    # Create engine and search
    engine = SearchEngine(config)
    matches, _ = engine.search(text, patterns)
    return matches


def fuzzy_search(
    text: str,
    patterns: str | list[str],
    min_similarity: float = 0.6,
    max_results: int = 100,
) -> list[SearchMatch]:
    """
    Perform fuzzy (approximate) search only.

    Use this when you specifically want approximate matching, or when you know
    exact matching won't work (e.g., searching for text with typos).

    Args:
        text (str): Text to search in
        patterns (str | list[str]): Pattern(s) to search for
        min_similarity (float): Minimum similarity ratio (0.0 to 1.0).
            - 1.0 = exact match only
            - 0.8 = allows ~20% character differences
            - 0.6 = allows ~40% character differences
        max_results (int): Maximum number of results to return

    Returns:
        list[SearchMatch]: List of fuzzy matches, sorted by similarity (best first)

    Examples:
        >>> # Find "Python" even with typos
        >>> matches = fuzzy_search("I love Pythn programming", "Python", min_similarity=0.8)
        >>> print(f"Found '{matches[0].pattern}' with {matches[0].similarity:.1%} similarity")

        >>> # Search for multiple patterns with typos
        >>> text = "Progrming in Jva and Pythn"
        >>> matches = fuzzy_search(text, ["Programming", "Java", "Python"], min_similarity=0.7)
        >>> for match in matches:
        ...     print(f"{match.pattern}: {match.similarity:.1%}")
    """
    engine = SearchEngine()
    matches, _ = engine.search_fuzzy_only(text, patterns, min_similarity)
    return matches[:max_results]


def benchmark_algorithms(text: str, patterns: list[str]) -> dict[str, float]:
    """
    Benchmark all exact matching algorithms to find the fastest for your data.

    Use this to determine which algorithm works best for your specific text and
    pattern combinations.

    Args:
        text (str): Representative text sample
        patterns (list[str]): Representative patterns to search for

    Returns:
        dict[str, float]: Algorithm names mapped to execution times in seconds

    Example:
        >>> text = "Large document content..." * 1000
        >>> patterns = ["important", "keyword", "search"]
        >>> results = benchmark_algorithms(text, patterns)
        >>> fastest = min(results, key=results.get)
        >>> print(f"Fastest algorithm: {fastest} ({results[fastest]:.4f}s)")
        >>>
        >>> # Use the fastest algorithm for your searches
        >>> matches = search_text(text, patterns, algorithm=fastest.lower().replace(' ', '_'))
    """
    engine = SearchEngine()
    return engine.benchmark_algorithms(text, patterns)


# Export all public interfaces
__all__ = [
    # Core interfaces and data structures
    "PatternSearcher",  # Abstract base class for all searchers
    "SearchMatch",  # Result data structure
    "SearchStrategy",  # Enum: EXACT or FUZZY
    # Main search engine and configuration
    "SearchEngine",  # Main search engine class
    "SearchConfig",  # Configuration options
    "SearchStats",  # Search execution statistics
    "AlgorithmType",  # Enum of exact matching algorithms
    # Individual algorithm implementations
    "KMPSearcher",  # Knuth-Morris-Pratt
    "BoyerMooreSearcher",  # Boyer-Moore (simple/complex)
    "AhoCorasickSearcher",  # Aho-Corasick multi-pattern
    "FuzzySearcher",  # Fuzzy/approximate search
    # Factory and convenience functions
    "create_searcher",  # Factory for individual algorithms
    "search_text",  # Main high-level search function
    "fuzzy_search",  # Fuzzy search convenience function
    "benchmark_algorithms",  # Performance benchmarking
]

# Package metadata
__version__ = "1.0.0"
__author__ = "RMDW (L)"
__description__ = "Unified interface for string matching algorithms with exact and fuzzy search capabilities"
