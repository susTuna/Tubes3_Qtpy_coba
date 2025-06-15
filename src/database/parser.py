import re

def process_resume_text(resume_text_content: str):
    
    # Find Skills section
    skills_pattern = re.findall(r'(Skills|Highlights)(.*?)(Work History|Experience|Education|Projects|$)', 
                              resume_text_content, flags=re.DOTALL | re.IGNORECASE)
    if skills_pattern:
        skills_text = skills_pattern[0][1].strip()
        # Split skills by commas or whitespace
        skills = []
        # First try splitting by commas if they exist
        if ',' in skills_text:
            skills = [s.strip() for s in skills_text.split(',') if s.strip()]
        else:
            # Otherwise split by whitespace for skill phrases
            skills = [s.strip() for s in skills_text.split() if s.strip()]
    else:
        skills = []
    
    # Find Experience section
    jobs = []
    job_pattern = re.findall(r'(Work History*|Experience*|Work Experience*)(.*?)(Education|Skills|Projects|$)', 
                           resume_text_content, flags=re.DOTALL | re.IGNORECASE)
    if job_pattern:
        job_text = job_pattern[0][1].strip()
        
        # Pattern for job entries: Job Title + Date Range + (optional Company) + Description
        job_entries = re.findall(
            r'([A-Za-z\s]+)\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+-\s+(?:Current|Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}))\s+([^,\n]*?)(?:,\s*([^,\n]*))?\n(.*?)(?=\n\n[A-Za-z\s]+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|Education|$)',
            job_text, 
            re.DOTALL
        )
        
        # If the complex pattern didn't work, try a simpler one
        if not job_entries:
            job_entries = re.findall(
                r'([A-Za-z\s]+)\n((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+-\s+(?:Current|Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}))\n(.*?)(?=\n[A-Za-z\s]+\n(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|Education|$)',
                job_text,
                re.DOTALL
            )
            
            # Process simple job format
            for job_title, job_period, job_desc in job_entries:
                jobs.append({
                    'title': job_title.strip(),
                    'period': job_period.strip(),
                    'company': 'Company Name',  # Not explicitly parsed
                    'location': 'Location',     # Not explicitly parsed
                    'description': job_desc.strip()
                })
        else:
            # Process complex job format
            for entry in job_entries:
                if len(entry) >= 5:  # Full match with company and location
                    job_title, job_period, company, location, job_desc = entry
                else:  # Partial match
                    job_title = entry[0]
                    job_period = entry[1]
                    company = entry[2] if len(entry) > 2 else 'Company Name'
                    job_desc = entry[-1]  # Last element is always description
                
                jobs.append({
                    'title': job_title.strip(),
                    'period': job_period.strip(),
                    'company': company.strip() if company else 'Company Name',
                    'location': location.strip() if 'location' in locals() else 'Location',
                    'description': job_desc.strip()
                })
    
    # Find Education section
    education = []
    edu_pattern = re.findall(r'(Education|Academic Background)(.*?)(Experience|Work History|Skills|$)', 
                           resume_text_content, flags=re.DOTALL | re.IGNORECASE)
    if edu_pattern:
        edu_text = edu_pattern[0][1].strip()
        
        # Try to match degree, field, institution and year
        edu_entries = re.findall(
            r'(Bachelor|Master|PhD|Doctor|B\.S\.|M\.S\.|M\.A\.|B\.A\.)(?:\s+of|\s+in)?\s+([^,\n]+)(?:,|\s+at|\s+from)\s+([^,\n]+)(?:,|\s+in|\s+)(?:.*?(\d{4}))?',
            edu_text,
            re.DOTALL | re.IGNORECASE
        )
        
        for entry in edu_entries:
            if len(entry) >= 3:
                degree_type = entry[0].strip()
                degree_field = entry[1].strip() if len(entry) > 1 else ""
                institution = entry[2].strip() if len(entry) > 2 else ""
                period = entry[3].strip() if len(entry) > 3 and entry[3] else ""
                
                education.append({
                    'degree': f"{degree_type} of {degree_field}",
                    'institution': institution,
                    'period': period,
                    'details': ""
                })
                
        # If no structured entries found, try a simpler approach
        if not education:
            # Look for line with university name followed by year
            uni_match = re.search(r'([A-Z][A-Za-z\s]+(?:University|College|Institute|School))[^\n]*?(\d{4})?', 
                                edu_text, re.IGNORECASE)
            if uni_match:
                institution = uni_match.group(1).strip()
                year = uni_match.group(2) if uni_match.group(2) else ""
                
                degree_match = re.search(r'(Bachelor|Master|PhD|Doctor|B\.S\.|M\.S\.|M\.A\.|B\.A\.)[^\n]*?([A-Za-z\s]+)', 
                                      edu_text, re.IGNORECASE)
                if degree_match:
                    degree_type = degree_match.group(1).strip()
                    field = degree_match.group(2).strip()
                    
                    education.append({
                        'degree': f"{degree_type} of {field}",
                        'institution': institution,
                        'period': year,
                        'details': ""
                    })
    return jobs, education, skills