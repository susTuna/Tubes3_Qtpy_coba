from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass(frozen=True)
class SearchMatch:
    """Unified match result structure."""

    pattern: str
    start_pos: int
    end_pos: int
    similarity: float = 1.0  # Always 1.0 for exact matches, variable for fuzzy

    @property
    def length(self) -> int:
        return self.end_pos - self.start_pos + 1


class SearchStrategy(Enum):
    """Search strategy types."""

    EXACT = "exact"
    FUZZY = "fuzzy"


class PatternSearcher(ABC):
    """Abstract base class for all pattern search algorithms."""

    @abstractmethod
    def search_multiple(self, text: str, patterns: List[str]) -> List[SearchMatch]:
        """
        Search for multiple patterns in text.

        Args:
            text: Text to search in
            patterns: List of patterns to search for

        Returns:
            List of SearchMatch objects sorted by position
        """
        pass

    def search_single(self, text: str, pattern: str) -> List[SearchMatch]:
        """
        Search for a single pattern in text.
        Default implementation delegates to search_multiple.
        """
        return self.search_multiple(text, [pattern])

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Return the name of the algorithm."""
        pass

    @property
    @abstractmethod
    def is_exact_match(self) -> bool:
        """Return True if this algorithm performs exact matching."""
        pass
