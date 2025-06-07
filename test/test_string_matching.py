import pytest # type: ignore
from src.algorithms.aho_corasick import AhoCorasick, _build_automaton, _search_multiple_patterns
from src.algorithms.kmp import kmp_search, _generate_lps_list
from src.algorithms.boyer_moore import boyer_moore_simple, boyer_moore_complex

class TestLSPGeneration:
    def test_simple_lsp(self):
        pattern = "aba"
        result = _generate_lps_list(pattern)
        assert result == [0, 0, 1]

    def test_complex_lsp(self):
        pattern = "ababaca"
        result = _generate_lps_list(pattern)
        assert result == [0, 0, 1, 2, 3, 0, 1]

    def test_no_prefix_suffix_match(self):
        pattern = "abcd"
        result = _generate_lps_list(pattern)
        assert result == [0, 0, 0, 0]

class TestKMPSearch:
    def test_simple_match(self):
        text = "hello world"
        pattern = "world"
        result = kmp_search(text, pattern)
        assert result == [6]

    def test_multiple_matches(self):
        text = "abababa"
        pattern = "aba"
        result = kmp_search(text, pattern)
        assert result == [0, 2, 4]

    def test_no_match(self):
        text = "hello world"
        pattern = "xyz"
        result = kmp_search(text, pattern)
        assert result == []

    def test_empty_pattern(self):
        text = "hello"
        pattern = ""
        result = kmp_search(text, pattern)
        assert result == []

    def test_empty_text(self):
        text = ""
        pattern = "hello"
        result = kmp_search(text, pattern)
        assert result == []

    def test_pattern_longer_than_text(self):
        text = "hi"
        pattern = "hello"
        result = kmp_search(text, pattern)
        assert result == []

class TestBoyerMooreSimpleSearch:
    def test_simple_match(self):
        text = "hello world"
        pattern = "world"
        result = boyer_moore_simple(text, pattern)
        assert result == [6]
    
    def test_multiple_matches(self):
        text = "abababa"
        pattern = "aba"
        result = boyer_moore_simple(text, pattern)
        assert result == [0, 2, 4]
    
    def test_no_match(self):
        text = "hello world"
        pattern = "xyz"
        result = boyer_moore_simple(text, pattern)
        assert result == []
    
    def test_empty_pattern(self):
        text = "hello"
        pattern = ""
        result = boyer_moore_simple(text, pattern)
        assert result == []
    
    def test_empty_text(self):
        text = ""
        pattern = "hello"
        result = boyer_moore_simple(text, pattern)
        assert result == []
    
    def test_pattern_longer_than_text(self):
        text = "hi"
        pattern = "hello"
        result = boyer_moore_simple(text, pattern)
        assert result == []


class TestBoyerMooreComplexSearch:
    def test_simple_match(self):
        text = "hello world"
        pattern = "world"
        result = boyer_moore_complex(text, pattern)
        assert result == [6]
    
    def test_multiple_matches(self):
        text = "abababa"
        pattern = "aba"
        result = boyer_moore_complex(text, pattern)
        assert result == [0, 2, 4]
    
    def test_no_match(self):
        text = "hello world"
        pattern = "xyz"
        result = boyer_moore_complex(text, pattern)
        assert result == []
    
    def test_empty_pattern(self):
        text = "hello"
        pattern = ""
        result = boyer_moore_complex(text, pattern)
        assert result == []
    
    def test_empty_text(self):
        text = ""
        pattern = "hello"
        result = boyer_moore_complex(text, pattern)
        assert result == []
    
    def test_pattern_longer_than_text(self):
        text = "hi"
        pattern = "hello"
        result = boyer_moore_complex(text, pattern)
        assert result == []


class TestAhoCorasick:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.ac = AhoCorasick()

    def test_empty_inputs(self):
        """Test behavior with empty inputs."""
        # Empty text
        self.ac.add_pattern("hello")
        assert self.ac.search("") == []
        
        # Empty pattern
        self.ac.add_pattern("")
        assert self.ac.search("hello world") == []
        
        # No patterns added
        empty_ac = AhoCorasick()
        assert empty_ac.search("hello world") == []

    def test_single_pattern_single_match(self):
        """Test searching for a single pattern with one occurrence."""
        self.ac.add_pattern("hello")
        result = self.ac.search("hello world")
        expected = [(0, 4, "hello")]
        assert result == expected

    def test_single_pattern_multiple_matches(self):
        """Test searching for a single pattern with multiple occurrences."""
        self.ac.add_pattern("ab")
        result = self.ac.search("ababab")
        expected = [(0, 1, "ab"), (2, 3, "ab"), (4, 5, "ab")]
        assert result == expected

    def test_multiple_patterns_basic(self):
        """Test searching for multiple patterns."""
        patterns = ["she", "he", "his", "hers"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("she sells his hersheys")
        expected = [
            (0, 2, "she"),
            (1, 2, "he"),
            (10, 12, "his"),
            (14, 16, "he")
        ]
        assert sorted(result) == sorted(expected)

    def test_overlapping_patterns(self):
        """Test patterns that overlap in the text."""
        patterns = ["abc", "bcd", "cde"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("abcde")
        expected = [
            (0, 2, "abc"),
            (1, 3, "bcd"),
            (2, 4, "cde")
        ]
        assert sorted(result) == sorted(expected)

    def test_pattern_within_pattern(self):
        """Test when one pattern is contained within another."""
        patterns = ["he", "she", "her", "hers"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("hershey")
        expected = [
            (0, 1, "he"),
            (0, 2, "her"),
            (0, 3, "hers")
        ]
        assert sorted(result) == sorted(expected)

    def test_case_sensitivity(self):
        """Test that the algorithm is case sensitive."""
        patterns = ["Hello", "hello", "HELLO"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("Hello hello HELLO")
        expected = [
            (0, 4, "Hello"),
            (6, 10, "hello"),
            (12, 16, "HELLO")
        ]
        assert sorted(result) == sorted(expected)

    def test_special_characters(self):
        """Test patterns with special characters."""
        patterns = ["@#$", "123", "a-b"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("test@#$123a-btest")
        expected = [
            (4, 6, "@#$"),
            (7, 9, "123"),
            (10, 12, "a-b")
        ]
        assert sorted(result) == sorted(expected)

    def test_unicode_characters(self):
        """Test patterns with Unicode characters."""
        patterns = ["café", "naïve", "résumé"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("I went to café and met a naïve person with résumé")
        expected = [
            (10, 13, "café"),
            (26, 30, "naïve"),
            (44, 49, "résumé")
        ]
        assert sorted(result) == sorted(expected)

    def test_no_matches(self):
        """Test when no patterns are found in the text."""
        patterns = ["xyz", "abc", "def"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("hello world")
        assert result == []

    def test_entire_text_is_pattern(self):
        """Test when the entire text is a pattern."""
        self.ac.add_pattern("hello")
        result = self.ac.search("hello")
        expected = [(0, 4, "hello")]
        assert result == expected

    def test_pattern_at_text_boundaries(self):
        """Test patterns at the beginning and end of text."""
        patterns = ["start", "end"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("start middle end")
        expected = [
            (0, 4, "start"),
            (13, 15, "end")
        ]
        assert sorted(result) == sorted(expected)

    def test_repeated_characters(self):
        """Test patterns with repeated characters."""
        patterns = ["aaa", "aa", "aaaa"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("aaaaa")
        expected = [
            (0, 1, "aa"),
            (0, 2, "aaa"),
            (0, 3, "aaaa"),
            (1, 2, "aa"),
            (1, 3, "aaa"),
            (2, 3, "aa"),
            (2, 4, "aaa"),
            (3, 4, "aa")
        ]
        assert sorted(result) == sorted(expected)

    def test_search_all_positions(self):
        """Test the search_all_positions method."""
        patterns = ["ab", "abc", "bc"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search_all_positions("abcabc")
        expected = {
            "ab": [(0, 1), (3, 4)],
            "abc": [(0, 2), (3, 5)],
            "bc": [(1, 2), (4, 5)]
        }
        assert result == expected

    def test_contains_any(self):
        """Test the contains_any method."""
        patterns = ["hello", "world"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        assert self.ac.contains_any("hello there") == True
        assert self.ac.contains_any("world peace") == True
        assert self.ac.contains_any("goodbye universe") == False

    def test_find_first_match(self):
        """Test the find_first_match method."""
        patterns = ["world", "hello"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.find_first_match("hello world")
        expected = (0, 4, "hello")  # Should find "hello" first
        assert result == expected
        
        # Test when no match is found
        result = self.ac.find_first_match("goodbye universe")
        assert result is None

    def test_convenience_functions(self):
        """Test the convenience functions."""
        patterns = ["cat", "dog", "bird"]
        text = "I have a cat and a dog but no bird"
        
        # Test _build_automaton
        ac = _build_automaton(patterns)
        result = ac.search(text)
        expected = [
            (9, 11, "cat"),
            (19, 21, "dog"),
            (30, 33, "bird")
        ]
        assert sorted(result) == sorted(expected)
        
        # Test _search_multiple_patterns
        result = _search_multiple_patterns(text, patterns)
        assert sorted(result) == sorted(expected)

    def test_dna_sequences(self):
        """Test with DNA-like sequences."""
        patterns = ["ATG", "TAA", "TGA", "TAG"]  # Start and stop codons
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        dna = "ATGCGATAAGTGACCTAG"
        result = self.ac.search(dna)
        expected = [
            (0, 2, "ATG"),
            (6, 8, "TAA"),
            (11, 13, "TGA"),
            (15, 17, "TAG")
        ]
        assert sorted(result) == sorted(expected)

    def test_performance_many_patterns(self):
        """Test performance with many patterns."""
        # Create 100 patterns
        patterns = [f"pattern{i}" for i in range(100)]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        # Create text containing some patterns
        text = "start " + " ".join(patterns[::10]) + " end"
        
        result = self.ac.search(text)
        # Should find 10 patterns (every 10th pattern)
        assert len(result) == 10

    def test_long_text(self):
        """Test with long text."""
        patterns = ["needle", "hay"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        # Create a long text with patterns at specific positions
        text = "hay" * 1000 + "needle" + "hay" * 1000
        result = self.ac.search(text)
        
        # Should find many "hay" occurrences and one "needle"
        needle_matches = [match for match in result if match[2] == "needle"]
        assert len(needle_matches) == 1
        assert needle_matches[0] == (3000, 3005, "needle")

    def test_duplicate_patterns(self):
        """Test adding duplicate patterns."""
        self.ac.add_pattern("hello")
        self.ac.add_pattern("hello")  # Add same pattern twice
        
        result = self.ac.search("hello world")
        # Should still work correctly, might have duplicates in output
        assert len(result) >= 1
        assert any(match[2] == "hello" for match in result)

    def test_very_long_pattern(self):
        """Test with a very long pattern."""
        long_pattern = "a" * 1000
        self.ac.add_pattern(long_pattern)
        
        text = "b" * 500 + "a" * 1000 + "b" * 500
        result = self.ac.search(text)
        expected = [(500, 1499, long_pattern)]
        assert result == expected

    def test_single_character_patterns(self):
        """Test with single character patterns."""
        patterns = ["a", "b", "c"]
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search("abcabc")
        expected = [
            (0, 0, "a"),
            (1, 1, "b"),
            (2, 2, "c"),
            (3, 3, "a"),
            (4, 4, "b"),
            (5, 5, "c")
        ]
        assert sorted(result) == sorted(expected)


# Parametrized tests for edge cases
class TestAhoCorasickParametrized:
    @pytest.mark.parametrize("text,patterns,expected_count", [
        ("", ["hello"], 0),  # Empty text
        ("hello", [""], 0),  # Empty pattern
        ("abc", ["xyz"], 0),  # No matches
        ("aaaa", ["aa"], 3),  # Overlapping matches
        ("hello world", ["hello", "world"], 2),  # Multiple patterns
    ])
    def test_parametrized_cases(self, text, patterns, expected_count):
        ac = AhoCorasick()
        for pattern in patterns:
            ac.add_pattern(pattern)
        
        result = ac.search(text)
        assert len(result) == expected_count

    @pytest.mark.parametrize("pattern,text,should_find", [
        ("hello", "hello world", True),
        ("xyz", "hello world", False),
        ("", "hello world", False),
        ("hello", "", False),
    ])
    def test_contains_any_parametrized(self, pattern, text, should_find):
        ac = AhoCorasick()
        if pattern:  # Only add non-empty patterns
            ac.add_pattern(pattern)
        
        result = ac.contains_any(text)
        assert result == should_find


# Performance and stress tests
class TestAhoCorasickPerformance:
    @pytest.mark.slow
    def test_large_number_of_patterns(self):
        """Test with a large number of patterns."""
        ac = AhoCorasick()
        patterns = [f"pattern{i}" for i in range(1000)]
        
        for pattern in patterns:
            ac.add_pattern(pattern)
        
        text = "This is a test with pattern500 and pattern999 in it"
        result = ac.search(text)
        
        assert len(result) == 2
        assert any(match[2] == "pattern500" for match in result)
        assert any(match[2] == "pattern999" for match in result)
    
    @pytest.mark.slow
    def test_very_long_text(self):
        """Test with very long text."""
        ac = AhoCorasick()
        patterns = ["needle", "haystack"]
        
        for pattern in patterns:
            ac.add_pattern(pattern)
        
        # Create 1MB of text
        text = "hay" * 100000 + "needle" + "stack" * 100000
        result = ac.search(text)
        
        needle_matches = [match for match in result if match[2] == "needle"]
        assert len(needle_matches) == 1


# Fixtures for complex test scenarios
@pytest.fixture
def dna_patterns():
    """Common DNA patterns for testing."""
    return ["ATG", "TAA", "TGA", "TAG", "CAT", "GCA"]

@pytest.fixture
def sample_dna_text():
    """Sample DNA text for testing."""
    return "ATGCGATAAGTGACCTAGCATGCA"

class TestAhoCorasickDNA:
    def test_dna_pattern_matching(self, dna_patterns, sample_dna_text):
        """Test DNA pattern matching using fixtures."""
        ac = AhoCorasick()
        for pattern in dna_patterns:
            ac.add_pattern(pattern)
        
        result = ac.search(sample_dna_text)
        
        # Should find multiple patterns
        assert len(result) > 0
        
        # Check specific patterns
        pattern_names = [match[2] for match in result]
        assert "ATG" in pattern_names
        assert "TAG" in pattern_names


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])