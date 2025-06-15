import re

def extract_section_content(resume_text: str, section_name: str) -> str:
    """
    Extracts the full text content of a specified resume section.

    Args:
        resume_text (str): The complete resume text.
        section_name (str): The name of the section to extract (e.g., "Work Experience", "Education").

    Returns:
        str: The raw text content of the section, or an empty string if not found.
    """
    # Define a comprehensive list of potential section headers for lookahead, including common variations.
    all_possible_section_headers = [
        "Work Experience", "Experience", "Work History",
        "Education", "Educational Background",
        "Skills", "Core Strengths", "Core Competencies",
        "Certifications", "Professional Affiliations",
        "Interests", "Additional Information",
        "Summary", "Professional Summary", "Core Qualifications",
        "Personal Information", "Languages", "Accomplishments",
        "Career Overview", "Highlights" # Added more potential section dividers
    ]

    # Dynamically build the lookahead part of the regex based on the section being extracted.
    lookahead_headers = [header for header in all_possible_section_headers if section_name.lower() not in header.lower()]
    # Ensure "Experience" is not included in lookahead if section_name is "Work Experience" and vice-versa
    if section_name.lower() == "experience":
        lookahead_headers = [h for h in lookahead_headers if h.lower() != "work experience" and h.lower() != "work history"]
    elif section_name.lower() == "work experience" or section_name.lower() == "work history":
        lookahead_headers = [h for h in lookahead_headers if h.lower() != "experience"]

    lookahead_pattern_str = "|".join(re.escape(h) for h in lookahead_headers)

    # Handle variations for Experience/Work Experience/Work History and Education/Educational Background
    if section_name == "Experience":
        section_start_pattern = r"(?:Work Experience|Experience|Work History)"
    elif section_name == "Education":
        section_start_pattern = r"(?:Education|Educational Background)"
    else:
        section_start_pattern = re.escape(section_name)

    # Construct the full regex pattern
    # re.DOTALL (re.S) allows '.' to match newlines.
    # re.IGNORECASE (re.I) makes the match case-insensitive for headers.
    # The lookahead is non-greedy (`.*?`) to stop at the *first* subsequent header.
    pattern = rf"{section_start_pattern}\s*(.*?)(?=\s*(?:{lookahead_pattern_str})\s*:|\Z)"

    match = re.search(pattern, resume_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def parse_job_entries(job_history_text: str) -> list[dict]:
    """
    Parses the raw job history text into a list of job dictionaries.

    Args:
        job_history_text (str): The raw text content of the job history section.

    Returns:
        list[dict]: A list of dictionaries, each representing a job with 'title', 'period', and 'description'.
    """
    jobs = []
    # This regex is designed to capture blocks starting with a potential job title.
    # It assumes a common structure:
    # Job Title (often capitalized, on its own line)
    # Optional Period (e.g., "Jan 2013 to Jan 2014")
    # Optional "Company Name" placeholder
    # Optional "City , State" placeholder
    # Description (everything else until the next job title pattern or end of section)

    job_regex = re.compile(
        # Capture Job Title (Group 'title') - starts a line, often capitalized, or looks like a title
        r"^(?P<title>[A-Za-z][\w\s.&,-/]+?)\s*$\n"
        # Optional Period (Group 'period') - flexible for "Mon Year" or "Mon Year to Mon Year/Current"
        r"(?:\s*(?P<period>(?:[A-Za-z]{3}\s*\d{4}|Present|Current)(?:\s*(?:to|-)\s*(?:[A-Za-z]{3}\s*\d{4}|Present|Current))?)\s*$\n)?"
        # Optional "Company Name" placeholder line (non-capturing group)
        r"(?:\s*Company Name\s*$\n)?"
        # Optional "City , State" placeholder line (non-capturing group)
        r"(?:\s*City\s*,\s*State\s*$\n)?"
        # Description (Group 'description') - non-greedy, matches anything until next job or end
        r"(?P<description>[\s\S]*?)"
        # Lookahead for the start of the next job entry (another capitalized title line) or end of string
        r"(?=\n^\s*[A-Za-z][\w\s.&,-/]+?\s*$|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    for match in job_regex.finditer(job_history_text):
        title = match.group('title').strip()
        period = match.group('period').strip() if match.group('period') else ''
        description = match.group('description').strip()

        # Further clean up description to remove lingering placeholders or excess newlines
        description = re.sub(r"^\s*Company Name\s*$", "", description, flags=re.MULTILINE | re.IGNORECASE).strip()
        description = re.sub(r"^\s*City\s*,\s*State\s*$", "", description, flags=re.MULTILINE | re.IGNORECASE).strip()
        
        # Remove empty lines in description
        description_lines = [line.strip() for line in description.split('\n') if line.strip()]
        description = '\n'.join(description_lines)

        jobs.append({
            'title': title,
            'period': period,
            'description': description
        })
    return jobs

def parse_education_entries(education_text: str) -> list[dict]:
    """
    Parses the raw education text into a list of education dictionaries.

    Args:
        education_text (str): The raw text content of the education section.

    Returns:
        list[dict]: A list of dictionaries, each representing an education entry
                    with 'degree', 'institution', and 'period'.
    """
    education_entries = []
    # This regex is designed to capture blocks starting with a potential degree title.
    # It assumes a structure like:
    # Degree (possibly with major, e.g., "Master's , Business Administration")
    # Optional Period (e.g., "2015")
    # Optional Institution Name
    # Optional Location ("City , State" and "USA")
    # Optional GPA line

    education_entry_regex = re.compile(
        # Capture Degree (Group 'degree') - flexible for various degree names and optional major
        r"^(?P<degree>(?:Master(?:'s)?|Bachelor(?:'s)?|Associate(?:'s)?|Diploma|Certificate|Coursework)(?:\s+of\s+[A-Za-z]+)?(?:\s*[,:]?\s*.+?)?)\s*$\n?"
        # Optional Period (Group 'period') - allows for year or year ranges, or just 'Current'
        r"(?:\s*\(?(?P<period>\d{4}(?:[-to]+\d{4})?|Current)\)?\s*$\n)?"
        # Optional Institution (Group 'institution') - captures until next placeholder or end of line
        r"(?:\s*(?P<institution>[A-Za-z][\w\s&.,'-]*?)\s*$\n)?"
        # Optional GPA line (non-capturing)
        r"(?:\s*GPA:.*?\s*$\n)?"
        # Optional "City , State" and "USA" placeholders (non-capturing)
        r"(?:\s*City\s*,\s*State(?:\s*,\s*USA)?\s*$\n)?"
        # Lookahead for the start of the next education entry (another degree line) or end of string
        r"(?=\n^\s*(?:Master(?:'s)?|Bachelor(?:'s)?|Associate(?:'s)?|Diploma|Certificate|Coursework)|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    for match in education_entry_regex.finditer(education_text):
        degree = match.group('degree').strip()
        period = match.group('period').strip() if match.group('period') else ''
        institution = match.group('institution').strip() if match.group('institution') else ''

        # Clean up any residual GPA or "City, State" from degree/institution if they snuck in
        degree = re.sub(r"(?:\s*GPA:.*|\s*City\s*,\s*State.*)", "", degree, flags=re.IGNORECASE).strip()
        institution = re.sub(r"(?:\s*GPA:.*|\s*City\s*,\s*State.*)", "", institution, flags=re.IGNORECASE).strip()
        
        education_entries.append({
            'degree': degree,
            'institution': institution,
            'period': period
        })
    return education_entries

# Example Usage (as provided by user to test with):
def process_resume_text(resume_text_content: str):
    """
    Processes a full resume text to extract structured job history and education.

    Args:
        resume_text_content (str): The full text content of a resume.

    Returns:
        tuple[list[dict], list[dict]]: A tuple containing lists for jobs and education.
    """
    # 1. Extract raw section contents
    job_history_raw = extract_section_content(resume_text_content, "Experience") # Using "Experience" as it's common
    education_raw = extract_section_content(resume_text_content, "Education")

    # 2. Parse individual entries from raw sections
    jobs = parse_job_entries(job_history_raw)
    education = parse_education_entries(education_raw)

    return jobs, education