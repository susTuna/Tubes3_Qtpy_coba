from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QScrollArea, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .general_config import gui_config
import datetime
import re

class CVSummaryWindow(QMainWindow):
    def __init__(
        self,
        name: str,
        birthdate,
        address: str,
        phone: str,
        skills,  # Can be string or list
        jobs,    # Can be string or list of dicts
        education  # Can be string or list of dicts
    ):
        super().__init__()
        self.setWindowTitle(f"CV Summary - {name}")
        self.setMinimumSize(700, 550)
        
        if isinstance(birthdate, datetime.date):
            birthdate = birthdate.strftime("%B %d, %Y")
        elif birthdate is None:
            birthdate = "Not provided"

        # Process inputs to ensure consistent format
        self.processed_skills = self._process_skills(skills)
        self.processed_jobs = self._process_jobs(jobs)
        self.processed_education = self._process_education(education)

        # Main scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Create each section
        self.create_header_section(main_layout, name, birthdate, address, phone)
        self.create_skills_section(main_layout, self.processed_skills)
        self.create_experience_section(main_layout, self.processed_jobs)
        self.create_education_section(main_layout, self.processed_education)
        
        # Add final spacer
        main_layout.addStretch()
    
    def _process_skills(self, skills):
        """Process skills input to ensure list format"""
        if isinstance(skills, str):
            # Split semicolon or comma-separated skills
            if ';' in skills:
                return [s.strip() for s in skills.split(';') if s.strip()]
            elif ',' in skills:
                return [s.strip() for s in skills.split(',') if s.strip()]
            else:
                return [skills]
        elif isinstance(skills, list):
            return skills
        else:
            return ["No skills found"]
    
    def _process_jobs(self, jobs):
        """Process jobs input to ensure consistent format"""
        processed_jobs = []
        
        if isinstance(jobs, str) and jobs != "Not Found":
            # Split by commas if it's a string
            job_items = [j.strip() for j in jobs.split(',') if j.strip()]
            
            for item in job_items:
                job = {
                    'title': item,
                    'period': 'Not specified',
                    'company': 'Not specified',
                    'location': 'Not specified',
                    'description': ''
                }
                processed_jobs.append(job)
        
        elif isinstance(jobs, list):
            # If it's already a list, ensure each item is a dict
            for job in jobs:
                if isinstance(job, dict):
                    processed_jobs.append(job)
                else:
                    processed_jobs.append({
                        'title': str(job),
                        'period': 'Not specified',
                        'company': 'Not specified',
                        'location': 'Not specified',
                        'description': ''
                    })
        
        return processed_jobs
    
    def _process_education(self, education):
        """Process education input to ensure consistent format"""
        processed_education = []
        
        if isinstance(education, str) and education != "Not Found":
            # Split by commas if it's a string
            edu_items = [e.strip() for e in education.split(',') if e.strip()]
            
            for item in edu_items:
                edu = {
                    'degree': 'Degree not specified',
                    'institution': item,
                    'period': '',
                    'details': ''
                }
                processed_education.append(edu)
        
        elif isinstance(education, list):
            # If it's already a list, ensure each item is a dict
            for edu in education:
                if isinstance(edu, dict):
                    processed_education.append(edu)
                else:
                    processed_education.append({
                        'degree': 'Degree not specified',
                        'institution': str(edu),
                        'period': '',
                        'details': ''
                    })
        
        return processed_education

    def create_header_section(self, parent_layout, name, birthdate, address, phone):
        """Create the profile header section with contact info"""
        # Profile header with gradient background
        header_container = QFrame()
        header_container.setFixedHeight(80)  # Increased height for better appearance
        header_container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 {gui_config.colors.primary}, 
                        stop:1 {gui_config.colors.secondary});
            border-radius: {gui_config.spacing.border_radius_medium}px;
        """)
        
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Name label
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            color: white;
            font-size: 24pt;
            font-weight: bold;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(name_label)
        
        parent_layout.addWidget(header_container)
        
        # Contact details section
        contact_box = QFrame()
        contact_box.setFrameShape(QFrame.Shape.StyledPanel)
        contact_box.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border: 1px solid {gui_config.colors.border_light};
        """)
        
        contact_layout = QHBoxLayout(contact_box)
        contact_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a grid for contact details
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)  # Make value column stretch
        details_grid.setHorizontalSpacing(15)
        details_grid.setVerticalSpacing(10)
        
        # Detail fields
        detail_fields = [
            ("Date of Birth", birthdate or "Not provided"),
            ("Address", address or "Not provided"),
            ("Phone", phone or "Not provided")
        ]
        
        for row, (field, value) in enumerate(detail_fields):
            field_label = QLabel(f"{field}:")
            field_label.setStyleSheet(f"""
                color: {gui_config.colors.text_secondary};
                font-weight: bold;
                font-size: 11pt;
            """)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"""
                color: {gui_config.colors.text_primary};
                font-size: 11pt;
            """)
            value_label.setWordWrap(True)
            
            details_grid.addWidget(field_label, row, 0)
            details_grid.addWidget(value_label, row, 1)
        
        contact_layout.addLayout(details_grid)
        parent_layout.addWidget(contact_box)

    def create_skills_section(self, parent_layout, skills):
        """Create the skills section with max 3 items per row"""
        # Section header
        header_label = self.create_section_header("Skills")
        parent_layout.addWidget(header_label)
        
        if not skills or skills == ["No skills found"]:
            empty_label = self.create_empty_section_label("No skills found in resume")
            parent_layout.addWidget(empty_label)
            return
        
        # Skills container
        skills_box = QFrame()
        skills_box.setFrameShape(QFrame.Shape.StyledPanel)
        skills_box.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border: 1px solid {gui_config.colors.border_light};
            padding: 10px;
        """)
        
        # Grid layout for skills with max 3 per row
        skills_layout = QGridLayout(skills_box)
        skills_layout.setContentsMargins(15, 15, 15, 15)
        skills_layout.setHorizontalSpacing(15)
        skills_layout.setVerticalSpacing(15)
        
        # Place skills in grid, 3 per row
        for i, skill in enumerate(skills):
            row = i // 3
            col = i % 3
            
            skill_chip = self.create_skill_chip(skill)
            skills_layout.addWidget(skill_chip, row, col)
        
        parent_layout.addWidget(skills_box)

    def create_skill_chip(self, skill_text):
        """Create a styled skill chip"""
        chip = QFrame()
        chip.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_secondary};
            border: 1px solid {gui_config.colors.border_light};
            border-left: 4px solid {gui_config.colors.secondary};  /* Use secondary for accent */
            border-radius: {gui_config.spacing.border_radius_small}px;
        """)
        
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(skill_text)
        label.setStyleSheet(f"""
            color: {gui_config.colors.text_primary};
            font-size: 11pt;
        """)
        layout.addWidget(label)
        
        return chip

    def create_experience_section(self, parent_layout, jobs):
        """Create the job experience section"""
        # Section header
        header_label = self.create_section_header("Professional Experience")
        parent_layout.addWidget(header_label)
        
        if not jobs:
            empty_label = self.create_empty_section_label("No work experience found in resume")
            parent_layout.addWidget(empty_label)
            return
        
        # Experience container
        experience_container = QWidget()
        experience_layout = QVBoxLayout(experience_container)
        experience_layout.setContentsMargins(0, 0, 0, 0)
        experience_layout.setSpacing(10)
        
        for job in jobs:
            job_card = self.create_job_card(job)
            experience_layout.addWidget(job_card)
        
        parent_layout.addWidget(experience_container)

    def create_job_card(self, job):
        """Create a card for a job entry"""
        job_box = QFrame()
        job_box.setFrameShape(QFrame.Shape.StyledPanel)
        job_box.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border-left: 5px solid {gui_config.colors.primary};  /* Use primary as accent */
            border-top: 1px solid {gui_config.colors.border_light};
            border-right: 1px solid {gui_config.colors.border_light};
            border-bottom: 1px solid {gui_config.colors.border_light};
        """)
        
        job_layout = QVBoxLayout(job_box)
        job_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title row
        title_label = QLabel(job['title'])
        title_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.primary};  /* Use primary for main text */
        """)
        title_label.setWordWrap(True)
        job_layout.addWidget(title_label)
        
        # Company and period row (if available)
        if job.get('company') and job['company'] != 'Not specified':
            company_period_layout = QHBoxLayout()
            
            company_label = QLabel(job['company'])
            company_label.setStyleSheet(f"""
                font-size: 12pt;
                color: {gui_config.colors.text_secondary};
                font-weight: bold;
            """)
            company_period_layout.addWidget(company_label)
            
            company_period_layout.addStretch()
            
            if job.get('period') and job['period'] != 'Not specified':
                period_label = QLabel(job['period'])
                period_label.setStyleSheet(f"""
                    font-size: 11pt;
                    font-style: italic;
                    color: {gui_config.colors.text_secondary};
                """)
                company_period_layout.addWidget(period_label)
            
            job_layout.addLayout(company_period_layout)
        
        # Description (if available)
        if job.get('description') and job['description']:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet(f"background-color: {gui_config.colors.border_light};")
            job_layout.addWidget(separator)
            
            desc_label = QLabel(job['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                font-size: 11pt;
                color: {gui_config.colors.text_primary};
                margin-top: 5px;
            """)
            job_layout.addWidget(desc_label)
        
        return job_box

    def create_education_section(self, parent_layout, education):
        """Create the education section"""
        # Section header
        header_label = self.create_section_header("Education")
        parent_layout.addWidget(header_label)
        
        if not education:
            empty_label = self.create_empty_section_label("No education information found in resume")
            parent_layout.addWidget(empty_label)
            return
        
        # Education container
        education_container = QWidget()
        education_layout = QVBoxLayout(education_container)
        education_layout.setContentsMargins(0, 0, 0, 0)
        education_layout.setSpacing(10)
        
        for edu in education:
            edu_card = self.create_education_card(edu)
            education_layout.addWidget(edu_card)
        
        parent_layout.addWidget(education_container)

    def create_education_card(self, edu):
        """Create a card for an education entry"""
        edu_box = QFrame()
        edu_box.setFrameShape(QFrame.Shape.StyledPanel)
        edu_box.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border-left: 5px solid {gui_config.colors.secondary};  /* Use secondary as accent */
            border-top: 1px solid {gui_config.colors.border_light};
            border-right: 1px solid {gui_config.colors.border_light};
            border-bottom: 1px solid {gui_config.colors.border_light};
        """)
        
        edu_layout = QVBoxLayout(edu_box)
        edu_layout.setContentsMargins(15, 15, 15, 15)
        
        # Institution
        institution_label = QLabel(edu['institution'])
        institution_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.primary};  /* Use primary for main text */
        """)
        institution_label.setWordWrap(True)
        edu_layout.addWidget(institution_label)
        
        # Degree and period (if available)
        if edu.get('degree') and edu['degree'] != 'Degree not specified':
            degree_period_layout = QHBoxLayout()
            
            degree_label = QLabel(edu['degree'])
            degree_label.setStyleSheet(f"""
                font-size: 12pt;
                color: {gui_config.colors.text_secondary};
                font-weight: bold;
            """)
            degree_period_layout.addWidget(degree_label)
            
            degree_period_layout.addStretch()
            
            if edu.get('period') and edu['period']:
                period_label = QLabel(edu['period'])
                period_label.setStyleSheet(f"""
                    font-size: 11pt;
                    font-style: italic;
                    color: {gui_config.colors.text_secondary};
                """)
                degree_period_layout.addWidget(period_label)
            
            edu_layout.addLayout(degree_period_layout)
        
        # Details (if available)
        if edu.get('details') and edu['details']:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet(f"background-color: {gui_config.colors.border_light};")
            edu_layout.addWidget(separator)
            
            details_label = QLabel(edu['details'])
            details_label.setWordWrap(True)
            details_label.setStyleSheet(f"""
                font-size: 11pt;
                color: {gui_config.colors.text_primary};
                margin-top: 5px;
            """)
            edu_layout.addWidget(details_label)
        
        return edu_box

    def create_section_header(self, title):
        """Create a styled section header"""
        header = QLabel(title)
        header.setStyleSheet(f"""
            font-size: 16pt;
            font-weight: bold;
            color: {gui_config.colors.primary};
            padding-bottom: 5px;
            border-bottom: 2px solid {gui_config.colors.secondary};
        """)
        return header
    
    def create_empty_section_label(self, text):
        """Create an empty state label for a section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border: 1px solid {gui_config.colors.border_light};
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {gui_config.colors.text_muted};
            font-style: italic;
            font-size: 12pt;
            padding: 10px;
        """)
        layout.addWidget(label)
        
        return frame