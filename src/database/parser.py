from typing import List

import re

class SectionScraper:
    '''Scrapes sections out of PDF dumps'''

    skill_sections = [
        "skills",
        "skill highlights",
        "summary of skills",
    ]

    experience_sections = [
        "work history",
        "work experience",
        "experience",
        "professional experience",
        "professional history",
    ]

    education_sections = [
        "education",
        "education and training",
        "educational background",
        "teaching experience",
        "corporate experience"
    ]

    sections = skill_sections + experience_sections + education_sections + [
        "summary",
        "highlights",
        "professional summary",
        "core qualifications",
        "languages",
        "professional profile",
        "relevant experience",
        "affiliations",
        "certifications",
        "qualifications",
        "accomplishments",
        "additional information",
        "core accomplishments",
        "career overview",
        "core strengths",
        "interests",
        "professional affiliations",
        "online profile",
        "certifications and trainings",
        "credentials",
        "personal information",
        "career focus",
        "executive profile",
        "military experience",
        "community service",
        "presentasions",
        "publications",
        "community leadership positions",
        "license",
        "computer skills",
        "presentations",
        "volunteer work",
        "awards and publications",
        "activities and honors",
        "volunteer associations",
    ]

    def remove_prefix(text: str, prefix: str) -> str:
        if prefix:
            if text.lower().startswith(prefix.lower()):
                return text[len(prefix):]
        return text
    
    def remove_suffix(text: str, suffix: str) -> str:
        if suffix:
            if text.lower().endswith(suffix.lower()):
                return text[:-len(suffix)]
        return text
    
    def _read(self, source) -> str:
        text = source
        
        return text

    def scrape_skills(self, source: str) -> str:
        text = self._read(source)
        res = re.search(f"\n({'|'.join(self.skill_sections)})(\n.*)+?(\n({'|'.join(self.sections)})\n|$)", text, re.IGNORECASE)
        if res:
            i, j = res.span()
            content: str = SectionScraper.remove_prefix(text[i:j].strip(), res.groups()[0])
            for header in SectionScraper.sections:
                content = SectionScraper.remove_suffix(content, header)
            
            # Transform bullet points to comma separated list
            output = ", ".join(content.strip().split("\n"))

            return output
        else:
            return "Not Found"

    def scrape_experience(self, source: str) -> str:
        text = self._read(source)
        res = re.search(f"\n({'|'.join(self.experience_sections)})(\n.*)+?(\n({'|'.join(self.sections)})\n|$)", text, re.IGNORECASE)
        if res:
            i, j = res.span()
            content: str = SectionScraper.remove_prefix(text[i:j].strip(), res.groups()[0])
            for header in SectionScraper.sections:
                content = SectionScraper.remove_suffix(content, header)
            
            # cheating by detecting "company name" to detect lines containing jobs
            lines = content.splitlines()
            output = []
            keywords = [
                "Director",
                "Manager",
                "Analyst",
                "Specialist",
                "Recruiter",
                "Representative",
                "Coordinator",
                "Lead",
                "Consultant",
                "Volunteer",
                "Assistant",
                "Technician",
                "Supervisor",
                "Associate",
                "Intern",
                "Counselor",
                "Advocate"
            ]
            for line in lines:
                for keyword in keywords:
                    if keyword in line.strip():
                        output.extend(re.findall(f"[A-Z][a-zA-Z ]*{keyword}[a-zA-Z ]*", line.strip()))
                        break
                    elif "company name" != line.lower().strip() and "company name" in line.lower().strip():
                        output.append(line)

            if output:
                return ", ".join(list(set(output)))
            else:
                return "Not Found"
        else:
            return "Not Found"

    def scrape_education(self, source: str) -> str:
        text = self._read(source)
        res = re.search(f"\n({'|'.join(self.education_sections)})(\n.*)+?(\n({'|'.join(self.sections)})\n|$)", text, re.IGNORECASE)
        if res:
            i, j = res.span()
            content = SectionScraper.remove_prefix(text[i:j].strip(), res.groups()[0])
            for header in SectionScraper.sections:
                content = SectionScraper.remove_suffix(content, header)
            
            # scrape universities
            regex: List[str] = []
            regex.extend(re.findall("university of [a-zA-Z ]+", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ university", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ college", content, re.IGNORECASE))
            regex.extend(re.findall("college of [a-zA-Z ]+", content, re.IGNORECASE))
            regex.extend(re.findall("([a-zA-Z ]* institute of [a-zA-Z ]+|[a-zA-Z ]+ institute)", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ high school", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ seminary", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ center", content, re.IGNORECASE))
            regex.extend(re.findall("[a-zA-Z ]+ training program", content, re.IGNORECASE))

            if regex:
                return ", ".join(list(set(regex)))
            else:
                return "Not Found"
        else:
            return "Not Found"

SectionScraper.sections.sort(key=lambda s: len(s), reverse=True)