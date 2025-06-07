def kmp_search(text: str, pattern: str) -> list[int]:
    result: list[int] = []
    lps: list[int] = _generate_lps_list(pattern)
    text_length: int = len(text)
    pattern_length: int = len(pattern)

    # Check for impossible case
    if not pattern or not text:
        return result
    if pattern_length > text_length:
        return result

    text_pointer: int = 0
    pattern_pointer: int = 0

    while text_pointer < text_length:
        if text[text_pointer] == pattern[pattern_pointer]:
            text_pointer += 1
            pattern_pointer += 1

            if pattern_pointer == pattern_length:
                result.append(text_pointer - pattern_pointer)
                pattern_pointer = lps[pattern_pointer - 1]
        else:
            if pattern_pointer != 0:
                pattern_pointer = lps[pattern_pointer - 1]
            else:
                text_pointer += 1

    return result


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
