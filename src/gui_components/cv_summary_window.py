from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt    
from .general_config import gui_config
import datetime

class CVSummaryWindow(QMainWindow):
    def __init__(
        self,
        name: str,
        birthdate,
        address: str,
        phone: str,
        skills: list[str],
        jobs: list[dict],
        education: list[dict]
    ):
        super().__init__()
        self.setWindowTitle(f"CV Summary - {name}")
        self.setMinimumSize(650, 500)
        
        if isinstance(birthdate, datetime.date):
            birthdate = birthdate.strftime("%B %d, %Y")

        # Main scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create each section
        self.create_header_section(main_layout, name, birthdate, address, phone)
        self.create_skills_section(main_layout, skills)
        self.create_experience_section(main_layout, jobs)
        self.create_education_section(main_layout, education)
        
        # Add final spacer
        main_layout.addStretch()

    def create_header_section(self, parent_layout, name, birthdate, address, phone):
        """Create the profile header section with contact info"""
        # Section header
        header_label = QLabel("Personal Information")
        header_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.text_primary};
            padding-bottom: 5px;
            border-bottom: 2px solid {gui_config.colors.secondary};
        """)
        parent_layout.addWidget(header_label)
        
        # Profile container
        profile_box = QFrame()
        profile_box.setFrameShape(QFrame.Shape.StyledPanel)
        profile_box.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_secondary};
            border-radius: {gui_config.spacing.border_radius_medium}px;
            border: 1px solid {gui_config.colors.border_medium};
        """)
        
        profile_layout = QHBoxLayout(profile_box)
        
        # Left side with name bar
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            background-color: {gui_config.colors.bg_primary}; 
            color: {gui_config.colors.text_primary}; 
            padding: {gui_config.spacing.padding_small}px; 
            font-size: {gui_config.fonts.size_normal}pt; 
            font-weight: {gui_config.fonts.weight_bold};
            border-radius: {gui_config.spacing.border_radius_small}px;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        profile_layout.addWidget(name_label, 1)
        
        # Right side with details
        details_widget = QWidget()
        details_layout = QGridLayout(details_widget)
        details_layout.setContentsMargins(15, 10, 10, 10)
        details_layout.setVerticalSpacing(8)
        
        # Icon and details setup
        detail_fields = [
            ("Date of Birth:", birthdate),
            ("Address:", address),
            ("Phone:", phone)
        ]
        
        for row, (field, value) in enumerate(detail_fields):
            label = QLabel(field)
            label.setStyleSheet(f"font-weight: bold; color: {gui_config.colors.text_secondary};")
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {gui_config.colors.text_primary};")
            value_label.setWordWrap(True)
            
            details_layout.addWidget(label, row, 0)
            details_layout.addWidget(value_label, row, 1)
        
        profile_layout.addWidget(details_widget, 2)
        parent_layout.addWidget(profile_box)

    def create_skills_section(self, parent_layout, skills):
        """Create the skills section with max 3 items per row"""
        # Section header
        header_label = QLabel("Skills")
        header_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.text_primary};
            padding-bottom: 5px;
            border-bottom: 2px solid {gui_config.colors.secondary};
            margin-top: 10px;
        """)
        parent_layout.addWidget(header_label)
        
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
        skills_layout.setHorizontalSpacing(10)
        skills_layout.setVerticalSpacing(10)
        
        # Place skills in grid, 3 per row
        for i, skill in enumerate(skills):
            row = i // 3
            col = i % 3
            
            chip = QPushButton(skill)
            chip.setEnabled(False)
            chip.setStyleSheet(f"""
                border-radius: 15px; 
                padding: 8px 15px; 
                background-color: {gui_config.colors.secondary}; 
                color: white;
                font-size: 10pt;
                text-align: center;
            """)
            skills_layout.addWidget(chip, row, col)
        
        parent_layout.addWidget(skills_box)

    def create_experience_section(self, parent_layout, jobs):
        """Create the job experience section"""
        # Section header
        header_label = QLabel("Professional Experience")
        header_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.text_primary};
            padding-bottom: 5px;
            border-bottom: 2px solid {gui_config.colors.bg_primary};
            margin-top: 10px;
        """)
        parent_layout.addWidget(header_label)
        
        for job in jobs:
            job_box = QFrame()
            job_box.setFrameShape(QFrame.Shape.StyledPanel)
            job_box.setStyleSheet(f"""
                background-color: white;
                border-radius: {gui_config.spacing.border_radius_medium}px;
                border: 1px solid {gui_config.colors.border_light};
                margin-bottom: 8px;
            """)
            
            job_layout = QVBoxLayout(job_box)
            job_layout.setContentsMargins(15, 15, 15, 15)
            
            # Header row with title and period
            header_layout = QHBoxLayout()
            
            title = QLabel(job['title'])
            title.setStyleSheet("font-weight: bold; font-size: 13pt;")
            header_layout.addWidget(title)
            
            header_layout.addStretch()
            
            period = QLabel(job.get('period', ''))
            period.setStyleSheet(f"font-style: italic; color: {gui_config.colors.text_secondary};")
            header_layout.addWidget(period)
            
            job_layout.addLayout(header_layout)
            
            # Company and location
            if job.get('company') and job.get('company') != 'Company Name':
                company_layout = QHBoxLayout()
                company = QLabel(job.get('company', ''))
                company.setStyleSheet(f"font-weight: bold; color: {gui_config.colors.text_secondary};")
                company_layout.addWidget(company)
                
                if job.get('location') and job.get('location') != 'Location':
                    location = QLabel(f"({job.get('location', '')})")
                    location.setStyleSheet(f"color: {gui_config.colors.text_secondary};")
                    company_layout.addWidget(location)
                
                company_layout.addStretch()
                job_layout.addLayout(company_layout)
            
            # Add horizontal separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet(f"background-color: {gui_config.colors.border_light}; margin: 8px 0;")
            job_layout.addWidget(separator)
            
            # Description
            if job.get('description'):
                desc = QLabel(job.get('description', ''))
                desc.setWordWrap(True)
                desc.setStyleSheet("margin-top: 8px;")
                job_layout.addWidget(desc)
            
            parent_layout.addWidget(job_box)

    def create_education_section(self, parent_layout, education):
        """Create the education section"""
        # Section header
        header_label = QLabel("Education")
        header_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {gui_config.colors.primary};
            padding-bottom: 5px;
            border-bottom: 2px solid {gui_config.colors.secondary};
            margin-top: 10px;
        """)
        parent_layout.addWidget(header_label)
        
        for edu in education:
            edu_box = QFrame()
            edu_box.setFrameShape(QFrame.Shape.StyledPanel)
            edu_box.setStyleSheet(f"""
                background-color: white;
                border-radius: {gui_config.spacing.border_radius_medium}px;
                border: 1px solid {gui_config.colors.border_light};
                margin-bottom: 8px;
            """)
            
            edu_layout = QVBoxLayout(edu_box)
            edu_layout.setContentsMargins(15, 15, 15, 15)
            
            # Header with degree and period
            header_layout = QHBoxLayout()
            
            degree = QLabel(edu['degree'])
            degree.setStyleSheet("font-weight: bold; font-size: 13pt;")
            header_layout.addWidget(degree)
            
            header_layout.addStretch()
            
            if edu.get('period'):
                period = QLabel(edu.get('period', ''))
                period.setStyleSheet(f"font-style: italic; color: {gui_config.colors.text_secondary};")
                header_layout.addWidget(period)
            
            edu_layout.addLayout(header_layout)
            
            # Institution
            institution = QLabel(edu['institution'])
            institution.setStyleSheet(f"font-weight: bold; color: {gui_config.colors.text_secondary};")
            edu_layout.addWidget(institution)
            
            # Add details if available
            if edu.get('details'):
                # Add horizontal separator
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet(f"background-color: {gui_config.colors.border_light}; margin: 8px 0;")
                edu_layout.addWidget(separator)
                
                details = QLabel(edu.get('details', ''))
                details.setWordWrap(True)
                details.setStyleSheet("margin-top: 8px;")
                edu_layout.addWidget(details)
            
            parent_layout.addWidget(edu_box)
