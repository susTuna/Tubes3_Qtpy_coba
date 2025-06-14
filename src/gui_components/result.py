from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QScrollArea, QFrame, QPushButton, QTextEdit,
                            QProgressBar, QSplitter, QMessageBox, QFileDialog, QGridLayout, QDialog, QFormLayout, QGroupBox, QDialogButtonBox)  # type: ignore
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve # type: ignore
from PyQt6.QtGui import QFont, QPalette, QTextCharFormat, QColor # type: ignore
from typing import Optional, List, Dict, Any
from ..service.searchservice import CVMatch
from ..database.models import SessionLocal, ApplicantProfile
from .general_config import gui_config, ResultConfig
import time
import subprocess
import platform
import os
from ..service.service_provider import get_search_service


class ConfigurableResultCard(QFrame):
    """Highly configurable individual result card widget."""
    
    # Signals - remove card_clicked & card_double_clicked signals
    # Keep only the signal needed for the "View PDF" functionality
    view_pdf_requested = pyqtSignal(str)  # Emit the PDF path when view button clicked
    
    def __init__(self, 
                 match_data: CVMatch, 
                 config: Optional[ResultConfig] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Configuration
        self.config = config or gui_config.result
        self.gui_config = gui_config
        
        # Data
        self.match_data = match_data
        self.db = SessionLocal()
        self.profile = self.db.query(ApplicantProfile).get(self.match_data.applicant_id)
        self.db.close()
        self.name = self.profile.first_name + " " + self.profile.last_name if self.profile else "Unknown Applicant"
        self.cv_path = self.match_data.cv_path
        self.score = self.match_data.score
        self.occurrences = self.match_data.occurrences
        
        # Remove is_selected property, as cards won't be selectable
        # self.is_selected = False
        
        # Animation
        self.animation: Optional[QPropertyAnimation] = None
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self) -> None:
        """Set up the result card UI with better horizontal space usage."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_small,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_small
        )
        layout.setSpacing(self.gui_config.spacing.margin_small)
        
        # Header section with name and match count
        header_layout = QHBoxLayout()
        
        # Applicant name header
        name_label = QLabel(self.name)
        name_label.setObjectName("applicantNameLabel")
        name_font = QFont(self.gui_config.fonts.family_primary)
        name_font.setBold(True)
        name_font.setPointSize(self.gui_config.fonts.size_medium)  # Slightly smaller
        name_label.setFont(name_font)
        
        # Matches count
        matches_label = QLabel(f"Matches: {self.score}")
        matches_label.setObjectName("matchesLabel")
        matches_font = QFont(self.gui_config.fonts.family_primary)
        matches_font.setPointSize(self.gui_config.fonts.size_small)
        matches_label.setFont(matches_font)
        
        header_layout.addWidget(name_label)
        header_layout.addStretch(1)
        header_layout.addWidget(matches_label)
        
        # Matched keywords section with better styling
        keywords_label = QLabel("Matched keywords:")
        keywords_label.setObjectName("matchedKeywordsLabel")
        keywords_label.setFont(QFont(self.gui_config.fonts.family_primary, weight=QFont.Weight.Bold))
        
        # Create keyword chips in a flow layout
        keywords_widget = QWidget()
        keywords_layout = QVBoxLayout(keywords_widget)
        keywords_layout.setContentsMargins(0, 0, 0, 0)
        keywords_layout.setSpacing(4)
        
        # Add each keyword with its occurrence count as a styled label
        for key in self.occurrences:
            occurrence_text = f"{self.occurrences.get(key)} occurrence{'s' if self.occurrences.get(key) > 1 else ''}"
            keyword_item = QLabel(f"• {key}: {occurrence_text}")
            keyword_item.setObjectName("keywordItem")
            keyword_item.setStyleSheet(f"""
                padding: 2px 5px;
                color: {self.gui_config.colors.text_primary};
                background-color: {self.gui_config.colors.bg_secondary};
                border-radius: 3px;
            """)
            keywords_layout.addWidget(keyword_item)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        details_btn = QPushButton("CV Summary")
        details_btn.setObjectName("detailsBtn")
        
        view_cv_btn = QPushButton("View CV")
        view_cv_btn.setObjectName("viewCVBtn")
        
        buttons_layout.addWidget(details_btn)
        buttons_layout.addWidget(view_cv_btn)
        
        # Add all elements to the main layout
        layout.addLayout(header_layout)
        layout.addWidget(keywords_label)
        layout.addWidget(keywords_widget)
        layout.addStretch(1)
        layout.addLayout(buttons_layout)
        
        # Connect button signals
        details_btn.clicked.connect(self.show_details)
        view_cv_btn.clicked.connect(self.open_pdf)
    
    def show_details(self) -> None:
        """Show details for this CV using CV Summary Window"""
        from .cv_summary_window import CVSummaryWindow
    
        # Get service directly
        service = get_search_service()
    
        # Now use the service directly
        cv_details = service.get_cv_details(self.match_data.resume_id)
    
        # Extract profile data with fallbacks
        name = self.name
        birthdate = self.profile.date_of_birth if self.profile.date_of_birth else "Not available"
        address = self.profile.address if self.profile.address else "Not available"
        phone = self.profile.phone_number if self.profile.phone_number else "Not available"
    
        # Placeholder data - in a real app, you'd extract these from the CV or database
        # You could add functions to parse CV text from self.match_data.cv_path
        skills = list(self.occurrences.keys())  # Use matched keywords as skills for demo
    
        jobs = cv_details.get("jobs", [])
    
        education = cv_details.get("education", [])
        # Create and show the summary window
        self.summary_window = CVSummaryWindow(
            name=name,
            birthdate=birthdate,
            address=address,
            phone=phone,
            skills=skills,
            jobs=jobs,
            education=education
        )
    
        # Show the window as non-modal
        self.summary_window.show()
    
    def open_pdf(self) -> None:
        """Open the CV PDF file with the system's default PDF viewer"""
        if not self.cv_path or not os.path.exists(self.cv_path):
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"The PDF file could not be found at:\n{self.cv_path}"
            )
            return
            
        try:
            # Use the appropriate command based on the operating system
            if platform.system() == 'Windows':
                os.startfile(self.cv_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.cv_path])
            else:  # Linux and other Unix-like systems
                subprocess.run(['xdg-open', self.cv_path])
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error Opening PDF", 
                f"Could not open the PDF file:\n{str(e)}"
            )
    
    def _highlight_pattern_in_snippet(self, text_edit: QTextEdit, pattern: str) -> None:
        """Highlight the pattern in the snippet text."""
        try:
            
            cursor = text_edit.textCursor()
            format = QTextCharFormat()
            format.setBackground(QColor(self.gui_config.colors.warning))
            format.setForeground(QColor(self.gui_config.colors.text_primary))
            
            # Find and highlight all occurrences
            text = text_edit.toPlainText()
            start = 0
            while True:
                pos = text.lower().find(pattern.lower(), start)
                if pos == -1:
                    break
                
                cursor.setPosition(pos)
                cursor.setPosition(pos + len(pattern), cursor.MoveMode.KeepAnchor)
                cursor.mergeCharFormat(format)
                start = pos + 1
                
        except Exception:
            # Fallback: just display without highlighting
            pass
    
    def apply_styling(self) -> None:
        """Apply CSS styling to the card."""
        base_style = f"""
        QFrame {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
            margin: {self.gui_config.spacing.margin_small}px;
        }}
        """
        
        # if self.config.card_hover_effect:
        #     base_style += f"""
        #     QFrame:hover {{
        #         border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.secondary};
        #         background-color: {self.gui_config.colors.bg_secondary};
        #     }}
        #     """
    
        # Label styles
        label_styles = f"""
        QLabel#applicantNameLabel {{
            color: {self.gui_config.colors.text_primary};
            font-weight: bold;
            margin-bottom: {self.gui_config.spacing.margin_medium}px;
            background-color: transparent;
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px;
        }}
        QLabel#matchedKeywordsLabel {{
            color: {self.gui_config.colors.text_primary};
            background-color: transparent;
            border: none;
            font-weight: bold;
        }}
        QLabel#keywordItem {{
            background-color: transparent;
            border: none;
            padding-left: {self.gui_config.spacing.padding_small}px;
        }}
        """
        
        # Button styles
        button_styles = f"""
        QPushButton {{
            background-color: {self.gui_config.colors.secondary};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
        }}
        QPushButton:hover {{
            background-color: {self.gui_config.colors.primary};
        }}
        QPushButton#detailsBtn {{
            background-color: {self.gui_config.colors.secondary};
        }}
        QPushButton#viewCVBtn {{
            background-color: {self.gui_config.colors.accent};
        }}
        """
        
        full_style = base_style + label_styles + button_styles
        
        # Apply custom card style if provided
        if self.config.custom_card_style:
            full_style += f"QFrame {{ {self.config.custom_card_style} }}"
        
        self.setStyleSheet(full_style)
    
    # def mousePressEvent(self, event) -> None:
    #     """Handle mouse press events."""
    #     if event.button() == Qt.MouseButton.LeftButton and self.config.enable_card_selection:
    #         self.set_selected(not self.is_selected)
    #         self.card_clicked.emit(self.match_data)
    #     super().mousePressEvent(event)
    
    # def mouseDoubleClickEvent(self, event) -> None:
    #     """Handle mouse double-click events."""
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.card_double_clicked.emit(self.match_data)
    #     super().mouseDoubleClickEvent(event)
    
    # def set_selected(self, selected: bool) -> None:
    #     """Set the selection state of the card."""
    #     self.is_selected = selected
    #     if selected:
    #         self.setStyleSheet(self.styleSheet() + f"""
    #         QFrame {{
    #             border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.primary} !important;
    #             background-color: {self.gui_config.colors.bg_secondary} !important;
    #         }}
    #         """)
    #     else:
    #         self.apply_styling()  # Reset to normal styling
    
    def animate_entry(self) -> None:
        """Animate card entry if animations are enabled."""
        if not self.config.enable_animations:
            return
            
        try:
            
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(300)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Start from slightly smaller size
            start_rect = self.geometry()
            start_rect.setHeight(int(start_rect.height() * 0.8))
            
            end_rect = self.geometry()
            
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)
            self.animation.start()
            
        except Exception:
            # Fallback: no animation
            pass
    
    def get_match_data(self) -> Dict[str, Any]:
        """Get the match data for this card."""
        return self.match_data.copy()


class ConfigurableResultsSection(QWidget):
    """Highly configurable results section displaying search results and statistics."""
    
    # Remove the selection-related signals
    export_requested = pyqtSignal(str)  # Emitted when export is requested with format
    results_cleared = pyqtSignal()  # Emitted when results are cleared
    
    def __init__(self, 
                 config: Optional[ResultConfig] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Configuration
        self.config = config or gui_config.result
        self.gui_config = gui_config
        
        # Data
        self.current_results: List[CVMatch] = []
        self.search_time: float = 0.0
        
        # Remove selected cards tracking
        # self.selected_cards: List[ConfigurableResultCard] = []
        
        # UI Elements
        self.results_title: Optional[QLabel] = None
        self.results_count_label: Optional[QLabel] = None
        self.search_time_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.export_btn: Optional[QPushButton] = None
        self.clear_results_btn: Optional[QPushButton] = None
        self.scroll_area: Optional[QScrollArea] = None
        self.scroll_content: Optional[QWidget] = None
        self.scroll_layout: Optional[QVBoxLayout] = None
        self.empty_state_label: Optional[QLabel] = None
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self) -> None:
        """Set up the results section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_small,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_small
        )
        layout.setSpacing(self.gui_config.spacing.margin_small)
        
        # Results header section
        if self.config.show_statistics:
            self.setup_results_header(layout)
        
        # Results content area
        self.setup_results_content(layout)
    
    def setup_results_header(self, parent_layout: QVBoxLayout) -> None:
        """Set up the results header with statistics."""
        # Header frame
        header_frame = QFrame()
        header_frame.setObjectName("resultsHeaderFrame")
        header_frame.setFrameStyle(QFrame.Shape.Box)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(self.gui_config.spacing.margin_medium)
        header_layout.setContentsMargins(
            self.gui_config.spacing.padding_medium,
            self.gui_config.spacing.padding_medium,
            self.gui_config.spacing.padding_medium,
            self.gui_config.spacing.padding_medium
        )
        
        # Title and stats row
        title_row = QHBoxLayout()
        
        # Results title
        self.results_title = QLabel(self.config.title_text)
        self.results_title.setObjectName("resultsTitle")
        
        title_font = QFont(self.gui_config.fonts.family_primary)
        title_font.setPointSize(self.gui_config.fonts.size_large)
        title_font.setBold(True)
        self.results_title.setFont(title_font)
        
        # Results count
        self.results_count_label = QLabel("No results")
        self.results_count_label.setObjectName("resultsCount")
        
        # Search time
        self.search_time_label = QLabel("⏱️ Time: --")
        self.search_time_label.setObjectName("searchTime")
        
        title_row.addWidget(self.results_title)
        title_row.addStretch()
        title_row.addWidget(self.results_count_label)
        title_row.addWidget(self.search_time_label)
        
        # Progress bar (for search indication)
        if self.config.show_progress_bar:
            self.progress_bar = QProgressBar()
            self.progress_bar.setObjectName("resultsProgressBar")
            self.progress_bar.setVisible(False)
        
        # Action buttons
        actions_row = QHBoxLayout()
        
        if self.config.show_export_button:
            self.export_btn = QPushButton(self.config.export_button_text)
            self.export_btn.setObjectName("exportBtn")
            self.export_btn.setEnabled(False)
            actions_row.addWidget(self.export_btn)
        
        if self.config.show_clear_button:
            self.clear_results_btn = QPushButton(self.config.clear_button_text)
            self.clear_results_btn.setObjectName("clearResultsBtn")
            self.clear_results_btn.setEnabled(False)
            actions_row.addWidget(self.clear_results_btn)
        
        actions_row.addStretch()
        
        header_layout.addLayout(title_row)
        if self.config.show_progress_bar:
            header_layout.addWidget(self.progress_bar)
        # header_layout.addLayout(actions_row)
        
        parent_layout.addWidget(header_frame)
        
        # Connect signals
        if self.export_btn:
            self.export_btn.clicked.connect(self.export_results)
        if self.clear_results_btn:
            self.clear_results_btn.clicked.connect(self.clear_results)
    
    def setup_results_content(self, parent_layout: QVBoxLayout) -> None:
        """Set up the scrollable results content area."""
        # Results scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("resultsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        
        # Scrollable content widget
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setObjectName("resultsScrollContent")
        self.scroll_layout.setObjectName("resultsScrollLayout")
        self.scroll_layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium
        )
        self.scroll_layout.setSpacing(self.gui_config.spacing.margin_small)
        
        # Empty state label
        self.empty_state_label = QLabel(self.config.empty_state_message)
        self.empty_state_label.setObjectName("emptyStateLabel")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_layout.addWidget(self.empty_state_label)
        self.scroll_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        parent_layout.addWidget(self.scroll_area)
    
    def apply_styling(self) -> None:
        """Apply CSS styling to all components."""
        # Header frame style
        header_style = f"""
        QFrame#resultsHeaderFrame {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
        }}
        """
        
        # Title and label styles
        title_styles = f"""
        QLabel#resultsTitle {{
            color: {self.gui_config.colors.text_primary};
        }}
        QLabel#resultsCount {{
            color: {self.gui_config.colors.text_secondary};
            font-weight: bold;
        }}
        QLabel#searchTime {{
            color: {self.gui_config.colors.warning};
            font-weight: bold;
        }}
        """
        
        # Button styles
        button_styles = f"""
        QPushButton#exportBtn {{
            background-color: {self.gui_config.colors.secondary};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#exportBtn:hover {{
            background-color: {self.gui_config.colors.primary};
        }}
        QPushButton#exportBtn:disabled {{
            background-color: {self.gui_config.colors.border_medium};
        }}
        
        QPushButton#clearResultsBtn {{
            background-color: {self.gui_config.colors.danger};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#clearResultsBtn:hover {{
            background-color: {self.gui_config.colors.accent};
        }}
        QPushButton#clearResultsBtn:disabled {{
            background-color: {self.gui_config.colors.border_medium};
        }}
        """
        
        # Scroll area style
        scroll_style = f"""
        QScrollArea#resultsScrollArea {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
        }}

        QWidget#resultsScrollContent {{
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
        }}

        QScrollBar:vertical, QScrollBar:horizontal {{
            border: none;
            background-color: {self.gui_config.colors.border_light};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal  {{
            background-color: {self.gui_config.colors.border_medium};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
            background-color: {self.gui_config.colors.text_secondary};
        }}
        """
        
        # Progress bar style
        progress_style = f"""
        QProgressBar#resultsProgressBar {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            text-align: center;
            font-weight: bold;
        }}
        QProgressBar#resultsProgressBar::chunk {{
            background-color: {self.gui_config.colors.secondary};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
        }}
        """
        
        # Empty state style
        empty_state_style = f"""
        QLabel#emptyStateLabel {{
            color: {self.gui_config.colors.text_secondary};
            font-size: {self.gui_config.fonts.size_large}pt;
            font-style: italic;
            padding: {self.gui_config.spacing.padding_large * 2}px;
            background-color: {self.gui_config.colors.bg_primary};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            border: {self.gui_config.spacing.border_width_medium}px dashed {self.gui_config.colors.border_medium};
        }}
        """
        
        # Combine all styles
        full_style = header_style + title_styles + button_styles + scroll_style + progress_style + empty_state_style
        
        # Apply custom styles if provided
        if self.config.custom_header_style:
            full_style += f"QFrame#resultsHeaderFrame {{ {self.config.custom_header_style} }}"
        
        if self.config.custom_empty_state_style:
            full_style += f"QLabel#emptyStateLabel {{ {self.config.custom_empty_state_style} }}"
        
        self.setStyleSheet(full_style)
    
    def show_search_progress(self, message: str = "Searching...") -> None:
        """Show search progress indication."""
        if self.progress_bar:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0) # Indeterminate progress
        
        if self.results_count_label:
            self.results_count_label.setText(message)
        if self.search_time_label:
            self.search_time_label.setText("⏱️ Time: --")
    
    def hide_search_progress(self) -> None:
        """Hide search progress indication."""
        if self.progress_bar:
            self.progress_bar.setVisible(False)
    
    def display_results(self, results: List[CVMatch], search_time: float, search_params: Dict[str, Any]) -> None:
        """Display search results with adaptive card sizing."""
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        
        # Clear previous results
        self.clear_results_display()
        self.current_results = results
        self.search_time = search_time
        
        # Update statistics
        if self.results_count_label:
            self.results_count_label.setText(f"Found: {len(results)} CV matches")
        
        if self.search_time_label:
            self.search_time_label.setText(f"⏱️ Time: {search_time:.3f}s")
        
        # Handle no results case by recreating the empty state label if needed
        if not results:
            # Always recreate the empty state label to avoid deleted widget issues
            # This ensures we have a fresh widget that hasn't been deleted
            self.empty_state_label = QLabel(self.config.no_results_message)
            self.empty_state_label.setObjectName("emptyStateLabel")
            self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.empty_state_label.setStyleSheet(f"""
                color: {self.gui_config.colors.text_secondary};
                font-size: {self.gui_config.fonts.size_large}pt;
                font-style: italic;
                padding: {self.gui_config.spacing.padding_large * 2}px;
                background-color: {self.gui_config.colors.bg_secondary};
                border-radius: {self.gui_config.spacing.border_radius_large}px;
                border: {self.gui_config.spacing.border_width_medium}px dashed {self.gui_config.colors.border_medium};
            """)
            
            # Add to layout
            self.scroll_layout.addWidget(self.empty_state_label)
            return
        
        # Create a container widget for all results
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(self.gui_config.spacing.margin_medium)
        
        # Get screen dimensions for responsive layout
        from PyQt6.QtWidgets import QApplication
        screen_width = QApplication.primaryScreen().size().width()
        
        # Calculate card width based on screen width
        card_width = min(500, max(300, int((screen_width - 100) / 3)))
        
        # Adaptive column count based on screen width
        max_cols = max(1, min(4, int(screen_width / 400)))  # 1-4 columns based on width
        
        # Create rows of cards
        row_idx = 0
        while row_idx < len(results):
            # Create a new row container with fixed size policy
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(self.gui_config.spacing.margin_medium)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Left align cards in row
            
            # Add cards to this row
            cards_in_row = 0
            for i in range(max_cols):
                if row_idx + i < len(results):
                    result = results[row_idx + i]
                    card = ConfigurableResultCard(result, self.config)
                    card.setMinimumWidth(card_width)
                    card.setMaximumWidth(card_width)
                    row_layout.addWidget(card)
                    cards_in_row += 1
                else:
                    break
            
            # Don't add any stretch to the row - let cards keep their size
            row_idx += cards_in_row
            results_layout.addWidget(row_widget)
        
        # Add the results container to the scroll area
        results_layout.addStretch()
        self.scroll_layout.addWidget(results_widget)
        
        # Update button states
        if self.export_btn:
            self.export_btn.setEnabled(True)
        if self.clear_results_btn:
            self.clear_results_btn.setEnabled(True)
        
        # Auto-scroll to results if enabled
        if self.config.auto_scroll_to_results and self.scroll_area:
            self.scroll_area.verticalScrollBar().setValue(0)
    
    def clear_results_display(self) -> None:
        """Clear the results display area."""
        # Remove all widgets except stretch
        while self.scroll_layout.count() > 0:
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Re-add empty state if no results
        if not self.current_results and self.empty_state_label:
            self.scroll_layout.addWidget(self.empty_state_label)
        
        self.scroll_layout.addStretch()
    
    def clear_results(self) -> None:
        """Clear all results and reset the display."""
        self.current_results.clear()
        self.search_time = 0.0
        
        # Reset UI
        if self.results_count_label:
            self.results_count_label.setText("No results")
        if self.search_time_label:
            self.search_time_label.setText("⏱️ Time: --")
        if self.export_btn:
            self.export_btn.setEnabled(False)
        if self.clear_results_btn:
            self.clear_results_btn.setEnabled(False)
        
        # Clear display
        self.clear_results_display()
        
        # Show empty state
        if self.empty_state_label and not self.empty_state_label.parent():
            self.scroll_layout.insertWidget(0, self.empty_state_label)
        
        self.results_cleared.emit()
    
    def export_results(self) -> None:
        """Export search results to a file."""
        if not self.current_results:
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Search Results",
            f"search_results_{int(time.time())}.{self.config.default_export_format}",
            self.config.supported_export_formats
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self._export_json(file_path)
                elif file_path.endswith('.csv'):
                    self._export_csv(file_path)
                else:  # .txt
                    self._export_txt(file_path)
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported successfully to:\n{file_path}"
                )
                
                # Get format from file extension
                export_format = file_path.split('.')[-1].lower()
                self.export_requested.emit(export_format)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Could not export results:\n{str(e)}"
                )
    
    def _export_json(self, file_path: str) -> None:
        """Export results as JSON."""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'search_time': self.search_time,
                'result_count': len(self.current_results),
                'results': self.current_results
            }, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, file_path: str) -> None:
        """Export results as CSV."""
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Pattern', 'Start Position', 'End Position', 'Snippet', 'Similarity'])
            for result in self.current_results:
                writer.writerow([
                    result.get('pattern', ''),
                    result.get('start_pos', ''),
                    result.get('end_pos', ''),
                    result.get('snippet', '').replace('\n', ' '),
                    result.get('similarity', '')
                ])
    
    def _export_txt(self, file_path: str) -> None:
        """Export results as plain text."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Search Results Export\n")
            f.write(f"{'='*50}\n")
            f.write(f"Search Time: {self.search_time:.3f} seconds\n")
            f.write(f"Total Matches: {len(self.current_results)}\n\n")
            
            for i, result in enumerate(self.current_results, 1):
                f.write(f"Match #{i}\n")
                f.write(f"Pattern: {result.get('pattern', 'N/A')}\n")
                f.write(f"Position: {result.get('start_pos', 0)}-{result.get('end_pos', 0)}\n")
                if 'similarity' in result:
                    f.write(f"Similarity: {result['similarity']:.1%}\n")
                f.write(f"Context: {result.get('snippet', 'N/A')}\n")
                f.write(f"{'-'*30}\n\n")
    
    # Public API methods
    def get_current_results(self) -> List[Dict[str, Any]]:
        """Get the current search results."""
        return self.current_results.copy()
    
    def get_search_time(self) -> float:
        """Get the last search time."""
        return self.search_time
    
    def update_config(self, config: ResultConfig) -> None:
        """Update result configuration and refresh UI."""
        self.config = config
        self.setup_ui()
        self.apply_styling()
    
    def set_theme(self, theme_name: str) -> None:
        """Apply a different theme to the results section."""
        self.gui_config.set_theme(theme_name)
        self.apply_styling()


# Backward compatibility - keep your original simple results
class ResultsSection(ConfigurableResultsSection):
    """Simple results section for backward compatibility."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)


class ResultCard(ConfigurableResultCard):
    """Simple result card for backward compatibility."""
    
    def __init__(self, match_data: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(match_data, parent=parent)