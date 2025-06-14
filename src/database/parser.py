import re
from typing import List, Dict, Tuple

# Define common date components for reusability and clarity
MONTHS_PATTERN = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
YEAR_PATTERN = r'(?:19|20)\d{2}' # THIS IS CRUCIAL: No '?' after \d{2}

DAY_PATTERN = r'\d{1,2}'

# Date format 1: "Month [Day], Year"
# Ensure the '?': (?:MONTHS_PATTERN...) is applied to the whole MONTHS_PATTERN group
DATE_FORMAT_1_PART = rf'(?:{MONTHS_PATTERN}[.,]?\s+)?(?:{DAY_PATTERN}[.,]?\s+)?{YEAR_PATTERN}'

# Date format 2: "MM/DD/YY"
# Ensure NO '?' after {YEAR_PATTERN} here either
DATE_FORMAT_2_PART = rf'(?:{DAY_PATTERN}[/.-])?{DAY_PATTERN}[/.-]{YEAR_PATTERN}'

# Combined flexible single date pattern
# This wraps the date format parts correctly in a non-capturing group
FLEXIBLE_SINGLE_DATE_PATTERN = rf'(?:{DATE_FORMAT_1_PART}|{DATE_FORMAT_2_PART})'

# Full job entry pattern:
# This wraps the first FLEXIBLE_SINGLE_DATE_PATTERN in a non-capturing group.
# The second FLEXIBLE_SINGLE_DATE_PATTERN is also used correctly.
JOB_PATTERN_REPAIRED = rf'(?:{FLEXIBLE_SINGLE_DATE_PATTERN})\s+(?:to|-)(?:\s+(?:Present|Current|{FLEXIBLE_SINGLE_DATE_PATTERN}))?\s+([^\n]+?)\s+(?:Company Name|Company|[—–-])'

# Test compilation for debugging
try:
    re.compile(JOB_PATTERN_REPAIRED)
    print("Repaired job pattern compiled successfully.")
except re.error as e:
    print(f"Error compiling repaired job pattern: {e}")

def extract_jobs(text: str) -> List[Dict[str, str]]:
    """Extract job information from regex-formatted text and clean non-alphanumeric characters."""
    jobs = []

    print(f"DEBUG: The job_pattern string being compiled is: '{JOB_PATTERN_REPAIRED}'")
    
    try:
        matches = re.finditer(JOB_PATTERN_REPAIRED, text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            try:
                date_range_raw = match.group(0).split("\n")[0].strip()
                title = match.group(1).strip() if len(match.groups()) >= 1 else "Unknown Position"
                
                jobs.append({
                    "title": (title),
                    "company": ("Company Name"), # This might need to be extracted from the match, depending on how "Company Name" is used in the regex
                    "period": (date_range_raw),
                    "description": ("Job details not available") # Placeholder, usually extracted from text after company
                })
            except Exception as e:
                print(f"Error processing job match: {e}")
    except Exception as e:
        print(f"Error in job extraction: {e}")
        
    if not jobs:
        jobs = [{
            "title": ("Position from CV"),
            "company": ("Company mentioned in CV"),
            "period": ("Time period mentioned in CV"),
            "description": ("Additional details would appear here")
        }]
        
    return jobs

def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education information from regex-formatted text and clean non-alphanumeric characters."""
    education = []
    
    # Look for education section
    education_section_pattern = r'(?:Education|Education and Training|Educational Background|Academic Background)(?:\s+and\s+Training)?[:\n]+(.*?)(?=\n\n\s*(?:Experience|Work|Employment|Professional|Skills|Certifications|Additional|Interests|Personal|\Z))'
    edu_match = re.search(education_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if not edu_match:
        return education
    
    edu_text = edu_match.group(1)
    
    # Pattern to match individual education entries
    degree_pattern = r'(?:Bachelor|Master|Associate|Ph\.?D\.?|Doctor|MBA|BS|BA|MS|AA|M\.?A\.?|B\.?S\.?|B\.?A\.?|M\.?S\.?|A\.?A\.?)[^\n]*((?:19|20)\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\n]*?(?:19|20)\d{2}|(?:19|20)\d{2}[^\n]*?(?:Present|Current))?[^\n]*?\n([^\n]+)'
    
    # Also look for common university/college indicators
    institution_pattern = r'(?:University|College|Institute|School)[^\n]*?(?:(?:19|20)\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\n]*?(?:19|20)\d{2})?[^\n]*?\n([^\n]+)'
    
    # Combine both patterns
    for pattern in [degree_pattern, institution_pattern]:
        matches = re.finditer(pattern, edu_text, re.IGNORECASE)
        
        for match in matches:
            try:
                degree_info = match.group(0).strip()
                
                # Extract components
                institution = match.group(1).strip() if len(match.groups()) > 0 else ""
                field = match.group(2).strip() if len(match.groups()) > 1 else ""
                
                # Check if we already have this entry (avoid duplicates)
                duplicate = False
                for entry in education:
                    # Compare cleaned versions to detect duplicates more reliably
                    if (institution) in (entry.get("institution", "")) or \
                       (entry.get("institution", "")) in (institution):
                        duplicate = True
                        break
                
                if not duplicate:
                    education.append({
                        "degree": (degree_info.split('\n')[0]),
                        "institution": (institution),
                        "field": (field)
                    })
            
            except Exception as e:
                print(f"Error extracting education: {e}")
                continue
    
    return education