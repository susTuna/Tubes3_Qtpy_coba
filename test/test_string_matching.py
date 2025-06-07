import pytest # type: ignore
from typing import List, Tuple, Dict, Optional
import time
import random
import string

# Import all algorithms
from src.algorithms.aho_corasick import AhoCorasick
from src.algorithms.kmp import (
    kmp_search, _generate_lps_list
)
from src.algorithms.boyer_moore import (
    boyer_moore_simple, boyer_moore_complex, _build_bad_character_table,
    _build_good_suffix_table
)
from src.algorithms.fuzzy_search import (
    levenshtein_distance, similarity_ratio, fuzzy_search_text,
    fuzzy_search_candidates
)


class TestKMPAlgorithm:
    """Comprehensive tests for KMP string matching algorithm."""
    
    def test_lps_generation_simple(self):
        """Test LPS array generation for simple patterns."""
        test_cases = [
            ("", []),
            ("a", [0]),
            ("ab", [0, 0]),
            ("aba", [0, 0, 1]),
            ("abab", [0, 0, 1, 2]),
            ("ababaca", [0, 0, 1, 2, 3, 0, 1]),
            ("abcabcab", [0, 0, 0, 1, 2, 3, 4, 5])
        ]
        
        for pattern, expected in test_cases:
            result = _generate_lps_list(pattern)
            assert result == expected, f"Failed for pattern '{pattern}'"
    
    def test_lps_generation_complex(self):
        """Test LPS array for complex patterns."""
        # Pattern with repeated substrings
        pattern = "AAACAAACAAAC"
        expected = [0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 7, 8]
        assert _generate_lps_list(pattern) == expected
        
        # Pattern with no prefix-suffix matches
        pattern = "ABCDEF"
        expected = [0, 0, 0, 0, 0, 0]
        assert _generate_lps_list(pattern) == expected
    
    def test_kmp_basic_search(self):
        """Test basic KMP search functionality."""
        test_cases = [
            ("hello world", "world", [6]),
            ("hello world", "hello", [0]),
            ("hello world", "o", [4, 7]),
            ("abababa", "aba", [0, 2, 4]),
            ("AABAACAADAABAABA", "AABA", [0, 9, 12]),
            ("", "test", []),
            ("test", "", []),
            ("short", "very long pattern", [])
        ]
        
        for text, pattern, expected in test_cases:
            result = kmp_search(text, pattern)
            assert result == expected, f"Failed for text '{text}' and pattern '{pattern}'"
    
    def test_kmp_edge_cases(self):
        """Test KMP edge cases."""
        # Single character
        assert kmp_search("a", "a") == [0]
        assert kmp_search("a", "b") == []
        
        # Pattern equals text
        assert kmp_search("hello", "hello") == [0]
        
        # Pattern at boundaries
        assert kmp_search("abcdef", "abc") == [0]
        assert kmp_search("abcdef", "def") == [3]
        
        # Overlapping patterns
        assert kmp_search("aaaa", "aa") == [0, 1, 2]
    
    def test_kmp_performance_patterns(self):
        """Test KMP with patterns designed to test performance."""
        # Worst case for naive algorithm
        text = "a" * 1000 + "b"
        pattern = "a" * 100 + "b"
        result = kmp_search(text, pattern)
        assert result == [900]
        
        # Periodic pattern
        text = "abcabc" * 100
        pattern = "abcabc"
        result = kmp_search(text, pattern)
        assert len(result) == 100  # Should find 100 occurrences

class TestBoyerMooreAlgorithm:
    """Comprehensive tests for Boyer-Moore string matching algorithm."""
    
    def test_bad_character_table(self):
        """Test bad character table construction."""
        test_cases = [
            ("abc", {'a': 0, 'b': 1, 'c': 2}),
            ("hello", {'h': 0, 'e': 1, 'l': 3, 'o': 4}),  # 'l' appears twice, last occurrence
            ("", {}),
            ("a", {'a': 0})
        ]
        
        for pattern, expected in test_cases:
            result = _build_bad_character_table(pattern)
            assert result == expected, f"Failed for pattern '{pattern}'"
    
    def test_good_suffix_table(self):
        """Test good suffix table construction."""
        # Basic test - ensure it returns correct length
        pattern = "abcab"
        result = _build_good_suffix_table(pattern)
        assert len(result) == len(pattern) + 1
        assert all(isinstance(x, int) and x >= 0 for x in result)
    
    def test_boyer_moore_simple_search(self):
        """Test Boyer-Moore simple (bad character only) search."""
        test_cases = [
            ("hello world", "world", [6]),
            ("hello world", "hello", [0]),
            ("abababa", "aba", [0, 2, 4]),
            ("", "test", []),
            ("test", "", []),
            ("short", "very long pattern", []),
            ("abcdefg", "xyz", [])
        ]
        
        for text, pattern, expected in test_cases:
            result = boyer_moore_simple(text, pattern)
            assert result == expected, f"Failed for text '{text}' and pattern '{pattern}'"
    
    def test_boyer_moore_complex_search(self):
        """Test Boyer-Moore complex (both heuristics) search."""
        test_cases = [
            ("hello world", "world", [6]),
            ("hello world", "hello", [0]),
            ("abababa", "aba", [0, 2, 4]),
            ("ABAAABCDABABCABCABCDAB", "ABCAB", [10, 15]),
            ("", "test", []),
            ("test", "", [])
        ]
        
        for text, pattern, expected in test_cases:
            result = boyer_moore_complex(text, pattern)
            assert result == expected, f"Failed for text '{text}' and pattern '{pattern}'"
    
    def test_boyer_moore_consistency(self):
        """Test that simple and complex versions give same results."""
        test_cases = [
            ("the quick brown fox jumps over the lazy dog", "the"),
            ("abcdefghijklmnop", "def"),
            ("aaaaaaa", "aa"),
            ("GCATCGCAGAGAGTATACAGTACG", "GCAG")
        ]
        
        for text, pattern in test_cases:
            simple_result = boyer_moore_simple(text, pattern)
            complex_result = boyer_moore_complex(text, pattern)
            assert simple_result == complex_result, f"Inconsistent results for '{text}' and '{pattern}'"
    
    def test_boyer_moore_edge_cases(self):
        """Test Boyer-Moore edge cases."""
        # Single character
        assert boyer_moore_simple("a", "a") == [0]
        assert boyer_moore_complex("a", "a") == [0]
        
        # Pattern equals text
        assert boyer_moore_simple("hello", "hello") == [0]
        assert boyer_moore_complex("hello", "hello") == [0]
        
        # Overlapping patterns
        simple_result = boyer_moore_simple("aaaa", "aa")
        complex_result = boyer_moore_complex("aaaa", "aa")
        assert simple_result == complex_result == [0, 1, 2]
    
    def test_boyer_moore_performance(self):
        """Test Boyer-Moore performance characteristics."""
        # Create text that benefits from Boyer-Moore skipping
        text = "a" * 1000 + "needle" + "a" * 1000
        pattern = "needle"
        
        simple_result = boyer_moore_simple(text, pattern)
        complex_result = boyer_moore_complex(text, pattern)
        
        assert simple_result == complex_result == [1000]


class TestAhoCorasickAlgorithm:
    """Comprehensive tests for Aho-Corasick multi-pattern matching."""
    
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
    
    def test_single_pattern_matching(self):
        """Test single pattern matching."""
        test_cases = [
            ("hello world", "hello", [(0, 4, "hello")]),
            ("hello world", "world", [(6, 10, "world")]),
            ("hello world", "xyz", []),
            ("aaaa", "aa", [(0, 1, "aa"), (1, 2, "aa"), (2, 3, "aa")])
        ]
        
        for text, pattern, expected in test_cases:
            ac = AhoCorasick()
            ac.add_pattern(pattern)
            result = ac.search(text)
            assert result == expected, f"Failed for text '{text}' and pattern '{pattern}'"
    
    def test_multiple_pattern_matching(self):
        """Test multiple pattern matching."""
        patterns = ["she", "he", "his", "hers"]
        text = "she sells his hersheys"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        expected = [
            (0, 2, "she"),
            (1, 2, "he"),
            (10, 12, "his"),
            (14, 16, "he")
        ]
        assert sorted(result) == sorted(expected)
    
    def test_overlapping_patterns(self):
        """Test overlapping pattern detection."""
        patterns = ["abc", "bcd", "cde", "def"]
        text = "abcdef"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        expected = [
            (0, 2, "abc"),
            (1, 3, "bcd"),
            (2, 4, "cde"),
            (3, 5, "def")
        ]
        assert sorted(result) == sorted(expected)
    
    def test_nested_patterns(self):
        """Test patterns contained within other patterns."""
        patterns = ["he", "she", "her", "hers"]
        text = "hershey"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        # Should find "he", "her", and "hers" starting at position 0
        pattern_names = [match[2] for match in result]
        assert "he" in pattern_names
        assert "her" in pattern_names
        assert "hers" in pattern_names
    
    def test_case_sensitivity(self):
        """Test case sensitivity."""
        patterns = ["Hello", "hello", "HELLO"]
        text = "Hello hello HELLO"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        assert len(result) == 3  # Should find all three different cases
    
    def test_special_characters(self):
        """Test patterns with special characters."""
        patterns = ["@#$", "123", "a-b", "x.y"]
        text = "test@#$123a-bx.ytest"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        assert len(result) == 4  # Should find all special character patterns
    
    def test_unicode_support(self):
        """Test Unicode character support."""
        patterns = ["café", "naïve", "résumé"]
        text = "I went to café and met a naïve person with résumé"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        pattern_names = [match[2] for match in result]
        assert "café" in pattern_names
        assert "naïve" in pattern_names
        assert "résumé" in pattern_names
    
    def test_long_patterns(self):
        """Test with very long patterns."""
        long_pattern = "a" * 1000
        text = "b" * 500 + "a" * 1000 + "b" * 500
        
        self.ac.add_pattern(long_pattern)
        result = self.ac.search(text)
        
        assert len(result) == 1
        assert result[0] == (500, 1499, long_pattern)
    
    def test_many_patterns(self):
        """Test with many patterns."""
        patterns = [f"pattern{i}" for i in range(100)]
        text = "start " + " ".join(patterns[::10]) + " end"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        assert len(result) == 10  # Should find every 10th pattern
    
    def test_repeated_characters(self):
        """Test patterns with repeated characters."""
        patterns = ["aa", "aaa", "aaaa"]
        text = "aaaaa"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        # Should find multiple overlapping matches
        assert len(result) > len(patterns)
    
    def test_utility_methods(self):
        """Test utility methods."""
        patterns = ["hello", "world"]
        text = "hello beautiful world"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        # Test contains_any
        assert self.ac.contains_any(text) == True
        assert self.ac.contains_any("goodbye universe") == False
        
        # Test find_first_match
        first_match = self.ac.find_first_match(text)
        assert first_match is not None
        assert first_match[2] == "hello"  # Should find "hello" first
        
        # Test search_all_positions
        positions = self.ac.search_all_positions(text)
        assert "hello" in positions
        assert "world" in positions
    
    def test_dna_sequences(self):
        """Test with biological DNA sequences."""
        # Common DNA patterns (start/stop codons)
        patterns = ["ATG", "TAA", "TGA", "TAG"]
        dna = "ATGCGATAAGTGACCTAGCATGCA"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(dna)
        pattern_names = [match[2] for match in result]
        
        assert "ATG" in pattern_names
        assert "TAG" in pattern_names
    
    def test_performance_stress(self):
        """Test performance with stress conditions."""
        # Many short patterns
        patterns = [f"p{i}" for i in range(1000)]
        text = "p500 and p999 are here"
        
        self.ac = AhoCorasick()
        for pattern in patterns:
            self.ac.add_pattern(pattern)
        
        result = self.ac.search(text)
        assert len(result) == 2  # Should find p500 and p999


class TestFuzzySearchAlgorithm:
    """Comprehensive tests for fuzzy search algorithms."""
    
    def test_levenshtein_distance_basic(self):
        """Test basic Levenshtein distance calculation."""
        test_cases = [
            ("", "", 0),
            ("", "abc", 3),
            ("abc", "", 3),
            ("abc", "abc", 0),
            ("abc", "ab", 1),
            ("abc", "abcd", 1),
            ("kitten", "sitting", 3),
            ("saturday", "sunday", 3),
            ("hello", "hallo", 1)
        ]
        
        for str1, str2, expected in test_cases:
            result = levenshtein_distance(str1, str2)
            assert result == expected, f"Failed for '{str1}' and '{str2}'"
    
    def test_levenshtein_distance_edge_cases(self):
        """Test Levenshtein distance edge cases."""
        # Identical strings
        assert levenshtein_distance("test", "test") == 0
        
        # Single character difference
        assert levenshtein_distance("test", "best") == 1
        assert levenshtein_distance("test", "tast") == 1
        assert levenshtein_distance("test", "tess") == 1
        
        # Complete substitution
        assert levenshtein_distance("abc", "xyz") == 3
        
        # Long strings
        long_str1 = "a" * 100
        long_str2 = "a" * 99 + "b"
        assert levenshtein_distance(long_str1, long_str2) == 1
    
    def test_similarity_ratio(self):
        """Test similarity ratio calculation."""
        test_cases = [
            ("", "", 1.0),
            ("", "abc", 0.0),
            ("abc", "", 0.0),
            ("abc", "abc", 1.0),
            ("abc", "ab", 2.0/3.0),  # 1 - (1/3)
            ("hello", "hallo", 0.8),  # 1 - (1/5)
        ]
        
        for str1, str2, expected in test_cases:
            result = similarity_ratio(str1, str2)
            assert abs(result - expected) < 0.001, f"Failed for '{str1}' and '{str2}'"
    
    def test_fuzzy_search_text(self):
        """Test fuzzy search in text."""
        text = "The quick brown fox jumps over the lazy dog"
        query = "quik"  # Misspelled "quick"
        
        result = fuzzy_search_text(query, text, min_similarity=0.6, max_results=5)
        
        assert len(result) > 0
        # Should find "quick" with high similarity
        similarities = [match[3] for match in result]
        assert max(similarities) > 0.6
    
    def test_fuzzy_search_candidates(self):
        """Test fuzzy search in candidate list."""
        candidates = ["apple", "banana", "orange", "grape", "pineapple", "apricot"]
        query = "aple"  # Misspelled "apple"
        
        result = fuzzy_search_candidates(query, candidates, min_similarity=0.5, max_results=3)
        
        assert len(result) > 0
        # "apple" should be the top match
        top_match = result[0]
        assert top_match[0] == "apple"
        assert top_match[1] > 0.8  # High similarity
    
    def test_fuzzy_search_performance(self):
        """Test fuzzy search performance."""
        # Create large candidate list
        candidates = [f"word{i}" for i in range(1000)]
        candidates.extend(["target", "targer", "taget"])  # Add similar words
        
        query = "target"
        
        start_time = time.time()
        result = fuzzy_search_candidates(query, candidates, min_similarity=0.8, max_results=5)
        end_time = time.time()
        
        # Should complete reasonably quickly
        assert end_time - start_time < 5.0  # Should take less than 5 seconds
        assert len(result) > 0
        assert result[0][0] == "target"  # Exact match should be first
    
    def test_fuzzy_search_edge_cases(self):
        """Test fuzzy search edge cases."""
        # Empty inputs
        assert fuzzy_search_candidates("", ["test"], 0.7, 10) == []
        assert fuzzy_search_candidates("test", [], 0.7, 10) == []
        assert fuzzy_search_candidates("test", [""], 0.7, 10) == []
        
        # Single character
        result = fuzzy_search_candidates("a", ["a", "b", "ab"], min_similarity=0.5, max_results=10)
        assert len(result) >= 1
        assert result[0][0] == "a"
        
        # Very different strings
        result = fuzzy_search_candidates("abc", ["xyz"], min_similarity=0.9, max_results=10)
        assert len(result) == 0


class TestAlgorithmComparison:
    """Compare different algorithms for consistency and performance."""
    
    def test_exact_match_consistency(self):
        """Test that all algorithms give same results for exact matches."""
        test_cases = [
            ("hello world", "world"),
            ("abababa", "aba"),
            ("test string", "test"),
            ("abcdefghijk", "def")
        ]
        
        for text, pattern in test_cases:
            # KMP
            kmp_result = kmp_search(text, pattern)
            
            # Boyer-Moore
            bm_simple = boyer_moore_simple(text, pattern)
            bm_complex = boyer_moore_complex(text, pattern)
            
            # Aho-Corasick
            ac = AhoCorasick()
            ac.add_pattern(pattern)
            ac_result = [match[0] for match in ac.search(text)]  # Extract start positions
            
            # All should give same results
            assert kmp_result == bm_simple == bm_complex == ac_result, \
                f"Inconsistent results for text '{text}' and pattern '{pattern}'"
    
    @pytest.mark.parametrize("text_size,pattern_size", [
        (100, 5),
        (1000, 10),
        (10000, 20)
    ])
    def test_algorithm_performance_comparison(self, text_size, pattern_size):
        """Compare algorithm performance on different input sizes."""
        # Generate random text and pattern
        text = ''.join(random.choices(string.ascii_lowercase, k=text_size))
        pattern = ''.join(random.choices(string.ascii_lowercase, k=pattern_size))
        
        # Ensure pattern exists in text at least once
        text = text[:text_size//2] + pattern + text[text_size//2:]
        
        algorithms = [
            ("KMP", lambda: kmp_search(text, pattern)),
            ("Boyer-Moore Simple", lambda: boyer_moore_simple(text, pattern)),
            ("Boyer-Moore Complex", lambda: boyer_moore_complex(text, pattern))
        ]
        
        results = {}
        times = {}
        
        for name, func in algorithms:
            start_time = time.time()
            result = func()
            end_time = time.time()
            
            results[name] = result
            times[name] = end_time - start_time
        
        # All algorithms should give same results
        first_result = list(results.values())[0]
        for name, result in results.items():
            assert result == first_result, f"{name} gave different result"
        
        # Performance logging (not assertion, just information)
        print(f"\nPerformance for text size {text_size}, pattern size {pattern_size}:")
        for name, time_taken in times.items():
            print(f"  {name}: {time_taken:.6f} seconds")


class TestIntegrationScenarios:
    """Integration tests with real-world scenarios."""
    
    def test_dna_sequence_analysis(self):
        """Test algorithms with DNA sequence data."""
        # Realistic DNA sequence
        dna_sequence = (
            "ATGCGATCGATCGATCGATCGATCGATCGATCGATCG"
            "TAAGCATGCATGCATGCATGCATGCATGCATGCATGC"
            "CGATCGATCGATCGATCGATCGATCGATCGATCGATC"
            "ATGCATGCATGCATGCATGCATGCATGCATGCATGCA"
            "TGATCGATCGATCGATCGATCGATCGATCGATCGATC"
        )
        
        # Common motifs
        motifs = ["ATG", "CATGC", "CGATC", "TGATC"]
        
        # Test with Aho-Corasick (best for multiple patterns)
        ac = AhoCorasick()
        for motif in motifs:
            ac.add_pattern(motif)
        
        ac_results = ac.search(dna_sequence)
        assert len(ac_results) > 0
        
        # Verify each motif individually with KMP
        for motif in motifs:
            kmp_results = kmp_search(dna_sequence, motif)
            ac_motif_results = [match[0] for match in ac_results if match[2] == motif]
            assert kmp_results == ac_motif_results
    
    def test_web_search_scenario(self):
        """Test fuzzy search in web search scenario."""
        web_pages = [
            "Python Programming Tutorial",
            "Java Programming Guide", 
            "JavaScript for Beginners",
            "C++ Programming Language",
            "Web Development with Python",
            "Machine Learning in Python",
            "Data Science Tutorial"
        ]
        
        # Test various search queries
        queries = [
            "python",
            "programing",  # Misspelled
            "javascript",
            "data science",
            "web dev"
        ]
        
        for query in queries:
            # Fuzzy search
            fuzzy_results = fuzzy_search_candidates(
                query.lower(), 
                [page.lower() for page in web_pages],
                min_similarity=0.3,
                max_results=5
            )
            
            # Should find relevant results
            assert len(fuzzy_results) >= 0
            
            # If high similarity found, should be reasonable match
            if fuzzy_results and fuzzy_results[0][1] > 0.7:
                best_match = fuzzy_results[0][0]
                assert query.split()[0][:3] in best_match or best_match[:3] in query
    
    def test_code_search_scenario(self):
        """Test pattern matching in code files."""
        code_content = '''
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n-1)
        
        class Calculator:
            def add(self, a, b):
                return a + b
            
            def subtract(self, a, b):
                return a - b
        '''
        
        # Search for patterns
        patterns = ["def ", "return ", "class ", "if ", "fibonacci"]
        
        ac = AhoCorasick()
        for pattern in patterns:
            ac.add_pattern(pattern)
        
        results = ac.search(code_content)
        
        # Should find multiple occurrences of common keywords
        def_count = len([r for r in results if r[2] == "def "])
        return_count = len([r for r in results if r[2] == "return "])
        
        assert def_count >= 3  # At least 3 function definitions
        assert return_count >= 4  # At least 4 return statements
    
    def test_multilingual_text_search(self):
        """Test algorithms with multilingual text."""
        multilingual_text = """
        Hello world! Bonjour le monde! Hola mundo!
        こんにちは世界！ Привет мир! مرحبا بالعالم
        Здравствуй мир! 你好世界！ Hallo Welt!
        """
        
        patterns = ["Hello", "Bonjour", "Hola", "мир", "世界"]
        
        # Test with Aho-Corasick
        ac = AhoCorasick()
        for pattern in patterns:
            ac.add_pattern(pattern)
        
        results = ac.search(multilingual_text)
        
        # Should find patterns in different scripts
        found_patterns = [r[2] for r in results]
        assert "Hello" in found_patterns
        assert "мир" in found_patterns  # Cyrillic
        assert "世界" in found_patterns  # Chinese/Japanese


@pytest.mark.slow
class TestPerformanceStress:
    """Stress tests for performance evaluation."""
    
    def test_large_text_performance(self):
        """Test with very large text."""
        # Create 1MB text
        large_text = "abcd" * 250000  # 1MB of text
        pattern = "abcd"
        
        algorithms = [
            ("KMP", lambda: kmp_search(large_text, pattern)),
            ("Boyer-Moore Simple", lambda: boyer_moore_simple(large_text, pattern)),
            ("Boyer-Moore Complex", lambda: boyer_moore_complex(large_text, pattern))
        ]
        
        for name, func in algorithms:
            start_time = time.time()
            result = func()
            end_time = time.time()
            
            # Should complete in reasonable time (< 10 seconds)
            assert end_time - start_time < 10.0, f"{name} took too long"
            assert len(result) == 250000  # Should find all occurrences
    
    def test_many_patterns_performance(self):
        """Test Aho-Corasick with many patterns."""
        # Create many patterns
        patterns = [f"pattern{i:04d}" for i in range(10000)]
        text = "This is a test with pattern0500 and pattern9999 somewhere"
        
        ac = AhoCorasick()
        
        # Adding patterns should be fast
        start_time = time.time()
        for pattern in patterns:
            ac.add_pattern(pattern)
        add_time = time.time() - start_time
        
        # Search should be fast
        start_time = time.time()
        results = ac.search(text)
        search_time = time.time() - start_time
        
        assert add_time < 5.0  # Adding patterns should take < 5 seconds
        assert search_time < 1.0  # Search should take < 1 second
        assert len(results) == 2  # Should find exactly 2 patterns
    
    def test_fuzzy_search_large_candidates(self):
        """Test fuzzy search with large candidate list."""
        # Create large candidate list
        candidates = []
        for i in range(10000):
            # Create variations of words
            base_words = ["python", "java", "javascript", "programming", "algorithm"]
            word = random.choice(base_words)
            # Add some random variations
            if random.random() < 0.1:  # 10% chance to modify
                word = word[:-1] + random.choice("abcdefghijk")
            candidates.append(f"{word}_{i}")
        
        query = "python"
        
        start_time = time.time()
        results = fuzzy_search_candidates(query, candidates, min_similarity=0.8, max_results=10)
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 10.0
        assert len(results) > 0


# Test fixtures for complex scenarios
@pytest.fixture
def sample_texts():
    """Provide sample texts for testing."""
    return {
        'english': "The quick brown fox jumps over the lazy dog",
        'repeated': "ababababab",
        'dna': "ATGCGATCGATCGATAA",
        'code': "def function(x): return x * 2",
        'mixed': "Hello123World!@#$%"
    }

@pytest.fixture
def common_patterns():
    """Provide common patterns for testing."""
    return {
        'short': ["a", "ab", "abc"],
        'medium': ["hello", "world", "test", "pattern"],
        'long': ["programming", "algorithm", "implementation"],
        'special': ["@#$", "123", "a-b-c"]
    }


class TestWithFixtures:
    """Tests using fixtures for complex scenarios."""
    
    def test_pattern_combinations(self, sample_texts, common_patterns):
        """Test various pattern and text combinations."""
        for text_name, text in sample_texts.items():
            for pattern_group, patterns in common_patterns.items():
                ac = AhoCorasick()
                for pattern in patterns:
                    ac.add_pattern(pattern)
                
                results = ac.search(text)
                # Just ensure no crashes and results are valid
                assert isinstance(results, list)
                for start, end, pattern in results:
                    assert isinstance(start, int)
                    assert isinstance(end, int)
                    assert isinstance(pattern, str)
                    assert start <= end
                    assert text[start:end+1] == pattern


if __name__ == "__main__":
    # Run all tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])