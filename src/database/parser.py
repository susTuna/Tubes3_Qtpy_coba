import re
from typing import Dict, List

# define some simple section-keywords
SECTION_KEYWORDS = {
    "job_history":   ["experience", "work history", "employment"],
    "education":     ["education", "academic", "degree"],
    "skills":        ["skills", "expertise", "technologies"]
}

def parse_for_regex(text: str) -> List[str]:
    """
    Parse the text line by line while keeping the original format.
    Including empty lines.
    """
    if not text:
        return []
    
    # Split by newline and preserve empty lines
    lines = [line.rstrip() for line in text.split('\n')]
    return lines

def parse_text(text: str) -> str:
    """
    Parse the entire text into a single lowercase string.
    """
    if not text:
        return ""
    
    # Convert to lowercase, replace newlines with spaces, normalize whitespace
    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_sections(full_text: str) -> Dict[str, str]:
    """
    Splits the resume text into job_history, education, skills
    by naive keyword matching. You can refine with regex or NLP.
    """
    sections = {k: "" for k in SECTION_KEYWORDS}
    lower = full_text.lower()

    for section, keys in SECTION_KEYWORDS.items():
        # find first occurrence of any keyword
        idxs = [lower.find(k) for k in keys if lower.find(k) != -1]
        if not idxs:
            continue
        start = min(idxs)
        # naive: take until next section keyword or end-of-text
        next_idxs = [
            lower.find(k2, start+1)
            for other, klist in SECTION_KEYWORDS.items() if other != section
            for k2 in klist
        ]
        end = min([i for i in next_idxs if i != -1], default=len(full_text))
        sections[section] = full_text[start:end].strip()
    return sections
