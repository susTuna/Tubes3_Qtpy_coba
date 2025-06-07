def kmp_search(text: str, pattern: str) -> list[int]:
    matches: list[int] = []
    lps: list[int] = _generate_lps_list(pattern)
    text_length: int = len(text)
    pattern_length: int = len(pattern)

    # Check for impossible case
    if not pattern or not text:
        return matches
    if pattern_length > text_length:
        return matches

    text_index: int = 0
    pattern_index: int = 0

    while text_index < text_length:
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == pattern_length:
                matches.append(text_index - pattern_index)
                pattern_index = lps[pattern_index - 1]
        else:
            if pattern_index != 0:
                pattern_index = lps[pattern_index - 1]
            else:
                text_index += 1

    return matches


def _generate_lps_list(pattern: str) -> list[int]:
    lps = [0] * len(pattern)
    length = 0
    pointer = 1 # lsp[0] is always 0, start from index 1

    while pointer < len(pattern):
        if pattern[pointer] == pattern[length]:
            length += 1
            lps[pointer] = length
            pointer += 1
        else:
            if length == 0:
                lps[pointer] = 0
                pointer += 1
            else:
                length = lps[length - 1]

    return lps
