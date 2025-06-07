from src.algorithms.kmp import kmp_search, _generate_lps_list

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