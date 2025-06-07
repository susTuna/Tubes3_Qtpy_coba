def _build_bad_character_table(pattern):
    bad_char = {}
    for i in range(len(pattern)):
        bad_char[pattern[i]] = i
    return bad_char

def _build_good_suffix_table(pattern):
    pattern_length = len(pattern)
    good_suffix = [0] * (pattern_length + 1)
    border = [0] * (pattern_length + 1)

    # Compute border array (similar to KMP failure function)
    pattern_index, suffix_index = pattern_length, pattern_length + 1
    border[pattern_index] = suffix_index

    while pattern_index > 0:
        while suffix_index <= pattern_length and pattern[pattern_index - 1] != pattern[suffix_index - 1]:
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

def boyer_moore_simple(text, pattern):
    text_length = len(text)
    pattern_length = len(pattern)
    matches = []

    if not pattern or not text:
        return matches

    if pattern_length > text_length:
        return matches

    # Build bad character table
    bad_char = _build_bad_character_table(pattern)

    shift = 0
    while shift <= text_length - pattern_length:
        pattern_index = pattern_length - 1

        # Match pattern from right to left
        while pattern_index >= 0 and pattern[pattern_index] == text[shift + pattern_index]:
            pattern_index -= 1

        if pattern_index < 0:
            # Pattern found
            matches.append(shift)
            # Shift to next possible position
            shift += pattern_length - bad_char.get(text[shift + pattern_length], -1) if shift + pattern_length < text_length else 1
        else:
            # Mismatch occurred, use bad character heuristic
            bad_char_shift = pattern_index - bad_char.get(text[shift + pattern_index], -1)
            shift += max(1, bad_char_shift)

    return matches

def boyer_moore_complex(text, pattern):
    text_length = len(text)
    pattern_length = len(pattern)
    matches = []

    if not pattern or not text:
        return matches

    if pattern_length > text_length:
        return matches

    # Build bad character and good suffix tables
    bad_char = _build_bad_character_table(pattern)
    good_suffix = _build_good_suffix_table(pattern)

    shift = 0
    while shift <= text_length - pattern_length:
        pattern_index = pattern_length - 1

        # Match pattern from right to left
        while pattern_index >= 0 and pattern[pattern_index] == text[shift + pattern_index]:
            pattern_index -= 1

        if pattern_index < 0:
            # Pattern found
            matches.append(shift)
            shift += good_suffix[0]
        else:
            # Mismatch occurred, use both heuristics
            bad_char_shift = pattern_index - bad_char.get(text[shift + pattern_index], -1)
            good_suffix_shift = good_suffix[pattern_index + 1]
            shift += max(bad_char_shift, good_suffix_shift)

    return matches