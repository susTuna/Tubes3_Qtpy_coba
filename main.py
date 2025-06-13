import sys
import traceback
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QLabel, QSizePolicy, QFrame, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt

from src.gui_components.header import HeaderComponent
from src.gui_components.search import SearchControls
from src.gui_components.result import ResultsSection
from src.search_algorithms.search_engine import SearchEngine, AlgorithmType
from src.database.models import SessionLocal, ApplicationDetail, ApplicantProfile
from src.database.pdf_utils import extract_text_from_pdf
from src.database.parser import parse_text
from src.config.config import CV_FOLDER

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applicant Tracking System")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Initialize components
        self.header = HeaderComponent()
        self.search_section = SearchControls()
        self.result_section = ResultsSection()
        self.status_label = QLabel("Ready. Enter a keyword to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add components to layout with proper spacing and separators
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.create_separator())
        main_layout.addWidget(self.search_section)
        main_layout.addWidget(self.create_separator())
        main_layout.addWidget(self.result_section)
        main_layout.addWidget(self.status_label)
        
        # Set proper size policies
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.search_section.setMinimumHeight(250)
        self.result_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Initialize search service and connect signals
        self.search_section.search_btn.clicked.connect(self.on_search)

    def create_separator(self):
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def on_search(self):
        """Handle search button click"""
        try:
            # Get search parameters from UI components
            keywords = self.search_section.get_keywords()
            if not keywords:
                self.update_status("Please enter at least one keyword.")
                return
                
            keyword = keywords[0] if keywords else ""
            algorithm = self.search_section.algorithm_combo.currentText()
            top_matches = self.search_section.top_matches_spin.value()
            
            # Update UI state
            self.update_status(f"Searching for: '{keyword}' using {algorithm}...")
            self.search_section.search_btn.setEnabled(False)
            
            # Perform search directly
            results, execution_time = self.perform_search(keyword, algorithm, top_matches)
            
            # Display results
            self.display_search_results(results, execution_time)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            print(f"Search error: {str(e)}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.search_section.search_btn.setEnabled(True)
    
    def perform_search(self, keyword, search_type, top_k):
        """Perform search directly in the main thread"""
        start_time = time.time()
        
        # Setup search engine
        search_engine = SearchEngine()
        
        # Get all resumes from database
        db = SessionLocal()
        resumes = db.query(ApplicationDetail).all()
        applicants = db.query(ApplicantProfile).all()
        db.close()
        
        # Create progress dialog
        progress = QProgressDialog("Searching resumes...", "Cancel", 0, len(resumes), self)
        progress.setWindowTitle("Search Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Initialize results
        results = {applicant.applicant_id: {"resumes": []} for applicant in applicants}
        
        # Map algorithm names to AlgorithmType
        algorithm_map = {
            "KMP (Knuth-Morris-Pratt)": AlgorithmType.KMP,
            "Boyer-Moore Simple": AlgorithmType.BOYER_MOORE_SIMPLE,
            "Boyer-Moore Complex": AlgorithmType.BOYER_MOORE_COMPLEX,
            "Aho-Corasick": AlgorithmType.AHO_CORASICK
        }
        
        # Process each resume
        for i, resume in enumerate(resumes):
            progress.setValue(i)
            progress.setLabelText(f"Processing resume: {resume.cv_file_name} ({i+1}/{len(resumes)})")
            
            # Check for cancellation
            if progress.wasCanceled():
                self.update_status("Search canceled by user.")
                return [], 0
                
            QApplication.processEvents()  # Keep UI responsive
            
            file_path = os.path.join(CV_FOLDER, resume.cv_file_name + ".pdf")
            if not os.path.exists(file_path):
                continue
                
            # Extract and parse text
            text = parse_text(extract_text_from_pdf(file_path))
            
            # Perform search based on algorithm type
            matches = []
            
            if "Fuzzy" in search_type:
                matches, _ = search_engine.search_fuzzy_only(text, keyword)
            else:
                algorithm = algorithm_map.get(search_type, AlgorithmType.AHO_CORASICK)
                matches, _ = search_engine.search_exact_only(text, keyword, algorithm)
            
            # If there are matches, add to results
            if matches:
                # Calculate overall score
                score = sum(match.similarity for match in matches)
                
                # Get context for matches
                match_data = []
                for match in matches[:5]:  # Top 5 matches per resume
                    context = self.get_context(text, match.start_pos, match.end_pos)
                    
                    match_data.append({
                        "keyword": match.pattern,
                        "start_pos": match.start_pos,
                        "end_pos": match.end_pos,
                        "similarity": match.similarity,
                        "context": context
                    })
                
                # Add to results
                results[resume.applicant_id]["resumes"].append({
                    "resume_id": resume.cv_file_name,
                    "score": score,
                    "file_path": file_path,
                    "matches": match_data
                })
        
        # Close progress dialog
        progress.setValue(len(resumes))
        
        # Sort results by total score
        sorted_results = sorted(
            results.items(),
            key=lambda item: sum(resume.get("score", 0) for resume in item[1]["resumes"]),
            reverse=True
        )
        
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Return only top-k results
        return sorted_results[:top_k], execution_time
    
    def get_context(self, text, start_pos, end_pos, context_chars=50):
        """Extract context around a match"""
        text_len = len(text)
        context_start = max(0, start_pos - context_chars)
        context_end = min(text_len, end_pos + context_chars)
        
        # Add ellipsis if needed
        prefix = "..." if context_start > 0 else ""
        suffix = "..." if context_end < text_len else ""
        
        return prefix + text[context_start:context_end] + suffix
    
    def display_search_results(self, results, execution_time):
        """Display search results"""
        try:
            # Convert results to correct format expected by ResultsSection
            formatted_results = []
            
            # results is a list of tuples: [(applicant_id, applicant_data), ...]
            for applicant_id, applicant_data in results:
                # Each applicant has a "resumes" list with match data
                for resume in applicant_data.get("resumes", []):
                    # Each resume has a "matches" list
                    for match in resume.get("matches", []):
                        formatted_results.append({
                            'pattern': match.get("keyword", ""),
                            'start_pos': match.get("start_pos", 0),
                            'end_pos': match.get("end_pos", 0),
                            'snippet': match.get("context", ""),
                            'similarity': match.get("similarity", 1.0),
                            'resume_id': resume.get("resume_id", ""),
                            'applicant_id': applicant_id
                        })
            
            # Update UI components with results
            self.result_section.display_results(
                formatted_results, 
                execution_time,
                {'algorithm': self.search_section.algorithm_combo.currentText()}
            )
            self.search_section.search_btn.setEnabled(True)
            
            # Show result count
            match_count = sum(len(data["resumes"]) for _, data in results)
            self.update_status(f"Search complete in {execution_time:.2f} seconds. Found {match_count} matches.")
            
        except Exception as e:
            self.update_status(f"Error displaying results: {str(e)}")
            print(f"Result display error: {str(e)}")
            traceback.print_exc()
            self.search_section.search_btn.setEnabled(True)

    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)

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

