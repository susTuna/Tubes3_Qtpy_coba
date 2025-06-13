import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

from .aho_corasick import AhoCorasickSearcher
from .boyer_moore import BoyerMooreSearcher
from .fuzzy_searcher import FuzzySearcher
from .kmp_searcher import KMPSearcher
from .pattern_searcher import PatternSearcher, SearchMatch, SearchStrategy


class AlgorithmType(Enum):
    """Available exact match algorithms."""

    KMP = "kmp"
    BOYER_MOORE_SIMPLE = "boyer_moore_simple"
    BOYER_MOORE_COMPLEX = "boyer_moore_complex"
    AHO_CORASICK = "aho_corasick"


@dataclass
class SearchConfig:
    """Search configuration parameters."""

    case_sensitive: bool = True
    max_results: int = 100
    exact_algorithm: AlgorithmType = AlgorithmType.AHO_CORASICK
    fuzzy_min_similarity: float = 0.6
    use_fuzzy_fallback: bool = True


@dataclass
class SearchStats:
    """Search execution statistics."""

    total_time: float
    exact_matches_count: int
    fuzzy_matches_count: int
    strategy_used: SearchStrategy
    algorithm_used: str
    patterns_searched: int


class SearchEngine:
    """
    Search engine that tries exact matching first,
    then falls back to fuzzy search if needed.
    """

    def __init__(self, config: SearchConfig = SearchConfig()):
        self.config = config
        self._exact_searchers: Dict[AlgorithmType, PatternSearcher] = {
            AlgorithmType.KMP: KMPSearcher(),
            AlgorithmType.BOYER_MOORE_SIMPLE: BoyerMooreSearcher(use_complex=False),
            AlgorithmType.BOYER_MOORE_COMPLEX: BoyerMooreSearcher(use_complex=True),
            AlgorithmType.AHO_CORASICK: AhoCorasickSearcher(),
        }
        self._fuzzy_searcher = FuzzySearcher(min_similarity=config.fuzzy_min_similarity)

    def search(
        self,
        text: str,
        patterns: Union[str, List[str]],
        config: Optional[SearchConfig] = None,
    ) -> tuple[List[SearchMatch], SearchStats]:
        """
        Unified search method with exact matching and fuzzy fallback.

        Args:
            text: Text to search in
            patterns: Pattern(s) to search for
            config: Optional search configuration (uses default if None)

        Returns:
            Tuple of (matches, search statistics)
        """
        # Use provided config or default
        search_config = config or self.config

        # Normalize patterns input
        if isinstance(patterns, str):
            pattern_list = [patterns]
        else:
            pattern_list = list(patterns)

        # Handle case sensitivity
        search_text = text if search_config.case_sensitive else text.lower()
        search_patterns = (
            pattern_list
            if search_config.case_sensitive
            else [p.lower() for p in pattern_list]
        )

        start_time = time.perf_counter()

        # Step 1: Try exact matching
        exact_searcher = self._exact_searchers[search_config.exact_algorithm]
        exact_matches = exact_searcher.search_multiple(search_text, search_patterns)

        # Step 2: Use fuzzy search if no exact matches and fallback is enabled
        fuzzy_matches: List[SearchMatch] = []
        strategy_used = SearchStrategy.EXACT

        if not exact_matches and search_config.use_fuzzy_fallback:
            self._fuzzy_searcher.set_similarity_threshold(
                search_config.fuzzy_min_similarity
            )
            fuzzy_matches = self._fuzzy_searcher.search_multiple(
                search_text, search_patterns
            )
            strategy_used = SearchStrategy.FUZZY

        end_time = time.perf_counter()

        # Combine results (exact matches take priority)
        all_matches = exact_matches + fuzzy_matches

        # Restore original case for patterns if needed
        if not search_config.case_sensitive:
            all_matches = self._restore_original_patterns(
                all_matches, pattern_list, search_patterns
            )

        # Limit results
        limited_matches = all_matches[: search_config.max_results]

        # Create statistics
        stats = SearchStats(
            total_time=end_time - start_time,
            exact_matches_count=len(exact_matches),
            fuzzy_matches_count=len(fuzzy_matches),
            strategy_used=strategy_used,
            algorithm_used=exact_searcher.algorithm_name,
            patterns_searched=len(pattern_list),
        )

        return limited_matches, stats

    def _restore_original_patterns(
        self,
        matches: List[SearchMatch],
        original_patterns: List[str],
        search_patterns: List[str],
    ) -> List[SearchMatch]:
        """Restore original case for patterns in search results."""
        pattern_mapping = dict(zip(search_patterns, original_patterns))

        restored_matches = []
        for match in matches:
            original_pattern = pattern_mapping.get(match.pattern, match.pattern)
            restored_match = SearchMatch(
                pattern=original_pattern,
                start_pos=match.start_pos,
                end_pos=match.end_pos,
                similarity=match.similarity,
            )
            restored_matches.append(restored_match)

        return restored_matches

    def search_exact_only(
        self,
        text: str,
        patterns: Union[str, List[str]],
        algorithm: AlgorithmType = AlgorithmType.AHO_CORASICK,
    ) -> tuple[List[SearchMatch], SearchStats]:
        """Search using only exact matching algorithms."""
        config = SearchConfig(exact_algorithm=algorithm, use_fuzzy_fallback=False)
        return self.search(text, patterns, config)

    def search_fuzzy_only(
        self, text: str, patterns: Union[str, List[str]], min_similarity: float = 0.6
    ) -> tuple[List[SearchMatch], SearchStats]:
        """Search using only fuzzy matching."""
        start_time = time.perf_counter()

        # Normalize patterns
        if isinstance(patterns, str):
            pattern_list = [patterns]
        else:
            pattern_list = list(patterns)

        # Set similarity and search
        self._fuzzy_searcher.set_similarity_threshold(min_similarity)
        matches = self._fuzzy_searcher.search_multiple(text, pattern_list)

        end_time = time.perf_counter()

        stats = SearchStats(
            total_time=end_time - start_time,
            exact_matches_count=0,
            fuzzy_matches_count=len(matches),
            strategy_used=SearchStrategy.FUZZY,
            algorithm_used=self._fuzzy_searcher.algorithm_name,
            patterns_searched=len(pattern_list),
        )

        return matches, stats

    def benchmark_algorithms(self, text: str, patterns: List[str]) -> Dict[str, float]:
        """Benchmark all exact matching algorithms."""
        results = {}

        for algo_type, searcher in self._exact_searchers.items():
            start_time = time.perf_counter()
            searcher.search_multiple(text, patterns)
            end_time = time.perf_counter()
            results[searcher.algorithm_name] = end_time - start_time

        return results

    def update_config(self, config: SearchConfig) -> None:
        """Update the search configuration."""
        self.config = config
        self._fuzzy_searcher.set_similarity_threshold(config.fuzzy_min_similarity)

    def get_available_algorithms(self) -> List[str]:
        """Get list of available exact matching algorithms."""
        return [searcher.algorithm_name for searcher in self._exact_searchers.values()]


# Convenience functions for quick searches
def search_text(
    text: str,
    patterns: Union[str, List[str]],
    algorithm: str = "aho_corasick",
    use_fuzzy_fallback: bool = True,
) -> List[SearchMatch]:
    """Quick search function with sensible defaults."""
    config = SearchConfig(
        exact_algorithm=AlgorithmType(algorithm.lower()),
        use_fuzzy_fallback=use_fuzzy_fallback,
    )
    engine = SearchEngine(config)
    matches, _ = engine.search(text, patterns)
    return matches


def fuzzy_search(
    text: str, patterns: Union[str, List[str]], min_similarity: float = 0.6
) -> List[SearchMatch]:
    """Quick fuzzy search function."""
    engine = SearchEngine()
    matches, _ = engine.search_fuzzy_only(text, patterns, min_similarity)
    return matches
