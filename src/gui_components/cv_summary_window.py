from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QApplication, QScrollArea
)
from PyQt6.QtCore import Qt

class CVSummaryWindow(QMainWindow):
    def __init__(
        self,
        name: str,
        birthdate: str,
        address: str,
        phone: str,
        skills: list[str],
        jobs: list[dict],
        education: list[dict]
    ):
        super().__init__()
        self.setWindowTitle("CV Summary")
        self.setMinimumSize(600, 400)

        # Scroll area in case content overflows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Personal Info
        info_box = QGroupBox()
        info_box.setStyleSheet("background-color: #e0e0e0; border: none;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Name header
        name_label = QLabel(name)
        name_label.setStyleSheet(
            "background-color: #555; color: white; padding: 8px; font-size: 16pt; font-weight: bold;"
        )
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(name_label)

        # Details
        detail_label = QLabel(
            f"Birthdate: {birthdate}\n"
            f"Address: {address}\n"
            f"Phone: {phone}"
        )
        detail_label.setStyleSheet("padding: 8px; font-size: 10pt;")
        info_layout.addWidget(detail_label)
        main_layout.addWidget(info_box)

        # Skills
        main_layout.addWidget(QLabel("Skills:"))
        skills_widget = QWidget()
        skills_layout = QHBoxLayout(skills_widget)
        skills_layout.setSpacing(5)
        for skill in skills:
            chip = QPushButton(skill)
            chip.setEnabled(False)
            chip.setStyleSheet(
                "border-radius: 10px; padding: 6px 12px; background-color: #c0c0c0; font-size: 9pt;"
            )
            skills_layout.addWidget(chip)
        main_layout.addWidget(skills_widget)

        # Job History
        main_layout.addWidget(QLabel("Job History:"))
        for job in jobs:
            job_box = QGroupBox()
            job_box.setStyleSheet("background-color: #e0e0e0; border: none;")
            job_layout = QVBoxLayout(job_box)
            job_layout.setContentsMargins(8, 8, 8, 8)

            title = QLabel(f"{job['title']}")
            title.setStyleSheet("font-weight: bold; font-size: 11pt;")
            job_layout.addWidget(title)

            period = QLabel(job.get('period', ''))
            period.setStyleSheet("font-style: italic; font-size: 9pt;")
            job_layout.addWidget(period)

            desc = QLabel(job.get('description', ''))
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 9pt; margin-top: 4px;")
            job_layout.addWidget(desc)

            main_layout.addWidget(job_box)

        # Education
        main_layout.addWidget(QLabel("Education:"))
        for edu in education:
            edu_box = QGroupBox()
            edu_box.setStyleSheet("background-color: #e0e0e0; border: none;")
            edu_layout = QVBoxLayout(edu_box)
            edu_layout.setContentsMargins(8, 8, 8, 8)

            deg = QLabel(f"{edu['degree']} ({edu['institution']})")
            deg.setStyleSheet("font-weight: bold; font-size: 11pt;")
            edu_layout.addWidget(deg)

            per = QLabel(edu.get('period', ''))
            per.setStyleSheet("font-size: 9pt; margin-top: 2px;")
            edu_layout.addWidget(per)

            main_layout.addWidget(edu_box)

        # Spacer
        main_layout.addStretch()
