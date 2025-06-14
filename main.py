import sys
import traceback
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QLabel, QSizePolicy, QFrame, QMessageBox, QProgressDialog,
                           QScrollArea)
from PyQt6.QtCore import Qt

from src.gui_components.header import HeaderComponent
from src.gui_components.search import SearchControls
from src.gui_components.result import ResultsSection
from src.service.searchservice import SearchService
from src.service.threadservice import PreprocessThread, SearchThread
from src.config.config import CV_FOLDER

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applicant Tracking System")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        self.service = SearchService()
        self.preprocess_cvs()

    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)
        
        # Initialize components
        self.header = HeaderComponent()
        self.search_section = SearchControls()
        self.result_section = ResultsSection()
        self.status_label = QLabel("Ready. Enter a keyword to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a scroll area for results
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setWidget(self.result_section)
        
        # Add components to layout with proper spacing and separators
        main_layout.addWidget(self.search_section)
        main_layout.addWidget(self.create_separator())
        main_layout.addWidget(self.results_scroll_area) # Use scroll area instead of result_section directly
        main_layout.addWidget(self.status_label)
        
        # Set proper size policies
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setMinimumHeight(250)
        self.result_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.results_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Add styling to scroll area
        self.results_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Initialize search service and connect signals
        self.search_section.search_requested.connect(self.on_search)

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
        
        # Update UI
        self.search_section.set_search_enabled(False)
        self.status_label.setText("Searching...")
        
        # Create progress dialog for search
        from PyQt6.QtWidgets import QProgressDialog
        self.search_progress = QProgressDialog("Searching CVs...", "Cancel", 0, 100, self)
        self.search_progress.setWindowTitle(f"Searching for: {keywords}")
        self.search_progress.setMinimumDuration(0)
        self.search_progress.setWindowModality(Qt.WindowModality.WindowModal)
        
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
            self.status_label.setText(
                f"Found {len(results)} matches among {total} CVs in {elapsed:.2f} seconds."
            )
        else:
            self.status_label.setText(
                f"No matches found among {total} CVs in {elapsed:.2f} seconds."
            )

    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)

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
        
        self.status_label.setText(f"Ready. {count} CVs preprocessed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    try:
        
        # Create and run application
        app = QApplication(sys.argv)
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

