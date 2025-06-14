import sys
import traceback
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QLabel, QSizePolicy, QFrame, QMessageBox, QProgressDialog,
                           QHBoxLayout)
from PyQt6.QtCore import Qt

from src.gui_components.header import HeaderComponent
from src.gui_components.search import SearchControls
from src.gui_components.result import ResultsSection
from src.service.searchservice import SearchService
from src.service.threadservice import PreprocessThread, SearchThread
from src.config.config import CV_FOLDER
from src.service.service_provider import set_search_service

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applicant Tracking System")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        
        # Create service and set it as global instance
        self.service = SearchService()
        set_search_service(self.service)
        
        self.preprocess_cvs()

    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # main_layout.setContentsMargins(20, 20, 20, 20)
        # main_layout.setSpacing(15)
        
        # Initialize components with better styling
        self.header = HeaderComponent(
        )
        
        self.search_section = SearchControls()
        self.result_section = ResultsSection()
        
        # Create a better status bar container
        status_container = QWidget()
        status_container.setObjectName("statusContainer")
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 5, 0, 0)
        status_layout.setSpacing(8)
        
        # Left status section (main message)
        self.status_label = QLabel("Ready. Enter keywords to begin searching.")
        self.status_label.setObjectName("statusLabel")
        
        # Right status section (CV count)
        self.cv_count_label = QLabel()
        self.cv_count_label.setObjectName("cvCountLabel")
        self.cv_count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Add to layout
        status_layout.addWidget(self.status_label, 3)  # Give more space to main status
        status_layout.addWidget(self.cv_count_label, 1)
        
        # Add components to layout with proper spacing
        # main_layout.addWidget(self.header)
        main_layout.addWidget(self.search_section)
        main_layout.addWidget(self.result_section)
        main_layout.addWidget(status_container)
        
        # Set proper size policies
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setMinimumHeight(250)
        self.result_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Initialize search service and connect signals
        self.search_section.search_requested.connect(self.on_search)

        # Apply application-wide styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            
            QScrollArea#resultsScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #bbbbbb;
                border-radius: 5px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #999999;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Make labels and buttons more modern */
            QLabel {
                color: #333333;
            }
            
            QPushButton {
                border-radius: 6px;
            }
                           
                           #statusContainer {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 8px 12px;
            }
            
            QLabel#statusLabel {
                color: #495057;
                font-size: 11px;
            }
            
            QLabel#cvCountLabel {
                color: #6c757d;
                font-size: 11px;
            }
            
            /* Status styles for different states */
            QLabel#statusLabel[state="info"] {
                color: #0d6efd;
            }
            
            QLabel#statusLabel[state="success"] {
                color: #198754;
            }
            
            QLabel#statusLabel[state="warning"] {
                color: #fd7e14;
            }
            
            QLabel#statusLabel[state="error"] {
                color: #dc3545;
            }
        """)

    def create_separator(self):
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def on_search(self, search_params):
        """Handle search button click with progress dialog"""
        keywords = search_params['keywords']
        algorithm = search_params['algorithm']
        top_k = search_params['top_matches']
        case_sensitive = search_params['case_sensitive']
        
        # Update UI with visual feedback
        self.search_section.set_search_enabled(False)
        
        # Animated status update
        self.status_label.setStyleSheet("""
            QLabel#statusLabel {
                color: #0066cc;
                font-size: 12px;
                padding: 8px;
                background-color: #e6f2ff;
                border-radius: 6px;
                border: 1px solid #99ccff;
                margin-top: 5px;
            }
        """)
        self.update_status("Searching CVs... Please wait", "info")
        
        # Create a more attractive progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        self.search_progress = QProgressDialog("Searching CVs...", "Cancel", 0, 100, self)
        self.search_progress.setWindowTitle(f"Searching for: {keywords}")
        self.search_progress.setMinimumDuration(0)
        self.search_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.search_progress.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border-radius: 10px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #4c72b0;
                border-radius: 5px;
            }
        """)
        
        # Create and start search thread using the imported class
        self.search_thread = SearchThread(
            self.service, keywords, algorithm, top_k, case_sensitive
        )
        self.search_thread.progress.connect(self.search_progress.setValue)
        self.search_thread.results_ready.connect(self.on_search_completed)
        self.search_thread.start()

    def on_search_completed(self, total, elapsed, results):
        """Handle completion of search"""
        self.search_section.set_search_enabled(True)
        
        # Close the progress dialog
        if hasattr(self, 'search_progress'):
            self.search_progress.close()
        
        # Display results
        self.result_section.display_results(
            results, elapsed, 
            {'keywords': self.search_section.get_keywords()}
        )
        
        # Update status
        if results:
            self.update_status(
                f"Found {len(results)} matches among {total} CVs in {elapsed:.2f} seconds.", 
                "success"
            )
        else:
            self.update_status(
                f"No matches found among {total} CVs in {elapsed:.2f} seconds.", 
                "warning"
            )

    def update_status(self, message, status_type="info"):
        """Update status message with proper styling"""
        # Set the status message
        self.status_label.setText(message)
        
        # Apply appropriate status style
        self.status_label.setProperty("state", status_type)
        
        # Force style refresh (needed for dynamic property changes)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def update_cv_count(self, count, preprocessed=False):
        """Update CV count in status bar"""
        if preprocessed:
            self.cv_count_label.setText(f"{count} CVs preprocessed")
        else:
            self.cv_count_label.setText(f"{count} CVs available")

    def preprocess_cvs(self):
        """Preprocess CVs in background thread with progress dialog"""
        # First, get count of files to process
        import os
        cv_files = [f for f in os.listdir(CV_FOLDER) if f.endswith('.pdf')]
        total_files = len(cv_files)
        
        # Create progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        self.preprocess_progress = QProgressDialog("Preprocessing CVs...", "Cancel", 0, total_files, self)
        self.preprocess_progress.setWindowTitle("CV Preprocessing")
        self.preprocess_progress.setMinimumDuration(0)  # Show immediately
        self.preprocess_progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        # Create and start thread using the imported class
        self.preprocess_thread = PreprocessThread(self.service)
        self.preprocess_thread.progress.connect(self.preprocess_progress.setValue)
        self.preprocess_thread.finished.connect(self.on_preprocessing_finished)
        self.preprocess_thread.start()
        
    def on_preprocessing_finished(self, count, elapsed):
        # Close the progress dialog
        if hasattr(self, 'preprocess_progress'):
            self.preprocess_progress.close()
        
        self.update_status(f"Ready to search", "info")
        self.update_cv_count(count, True)

if __name__ == "__main__":
    try:
        # Set application-wide style
        import sys
        from PyQt6.QtGui import QPalette, QColor
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        
        # Set app-wide font
        from PyQt6.QtGui import QFont
        font = QFont("Segoe UI", 10)  # Modern font
        app.setFont(font)
        
        # Create main window
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {str(e)}")
        traceback.print_exc()
        # Show error as message box
        if 'app' in locals():
            QMessageBox.critical(None, "Critical Error", 
                              f"The application could not start: {str(e)}")
            sys.exit(1)

