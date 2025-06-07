from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QScrollArea, QFrame, QPushButton, QTextEdit,
                            QProgressBar, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont, QPalette # type: ignore
from typing import Optional, List, Dict, Any
import time


class ResultCard(QFrame):
    """Individual result card widget."""
    
    def __init__(self, match_data: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.match_data = match_data
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the result card UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 5px;
            }
            QFrame:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Header with match info
        header_layout = QHBoxLayout()
        
        # Pattern/keyword found
        pattern_label = QLabel(f"🎯 Pattern: '{self.match_data.get('pattern', 'N/A')}'")
        pattern_font = QFont()
        pattern_font.setBold(True)
        pattern_font.setPointSize(11)
        pattern_label.setFont(pattern_font)
        pattern_label.setStyleSheet("color: #2c3e50;")
        
        # Position info
        start_pos = self.match_data.get('start_pos', 0)
        end_pos = self.match_data.get('end_pos', 0)
        position_label = QLabel(f"📍 Position: {start_pos}-{end_pos}")
        position_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        
        header_layout.addWidget(pattern_label)
        header_layout.addStretch()
        header_layout.addWidget(position_label)
        
        # Similarity/confidence (for fuzzy search)
        if 'similarity' in self.match_data:
            similarity = self.match_data['similarity']
            similarity_label = QLabel(f"💯 Similarity: {similarity:.1%}")
            similarity_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            header_layout.addWidget(similarity_label)
        
        # Context snippet
        snippet = self.match_data.get('snippet', '')
        if snippet:
            snippet_label = QLabel("📝 Context:")
            snippet_label.setStyleSheet("color: #34495e; font-weight: bold; margin-top: 5px;")
            
            snippet_text = QTextEdit()
            snippet_text.setPlainText(snippet)
            snippet_text.setReadOnly(True)
            snippet_text.setMaximumHeight(80)
            snippet_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ecf0f1;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 9pt;
                }
            """)
            
            layout.addLayout(header_layout)
            layout.addWidget(snippet_label)
            layout.addWidget(snippet_text)
        else:
            layout.addLayout(header_layout)
    
    def get_match_data(self) -> Dict[str, Any]:
        """Get the match data for this card."""
        return self.match_data


class ResultsSection(QWidget):
    """Results section displaying search results and statistics."""
    
    # Signals
    result_selected = pyqtSignal(dict)  # Emitted when a result is selected
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_results: List[Dict[str, Any]] = []
        self.search_time: float = 0.0
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the results section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)
        
        # Results header section
        self.setup_results_header(layout)
        
        # Results content area
        self.setup_results_content(layout)
    
    def setup_results_header(self, parent_layout: QVBoxLayout) -> None:
        """Set up the results header with statistics."""
        # Header frame
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)
        
        # Title and stats row
        title_row = QHBoxLayout()
        
        # Results title
        self.results_title = QLabel("📊 Search Results")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.results_title.setFont(title_font)
        self.results_title.setStyleSheet("color: #2c3e50;")
        
        # Results count
        self.results_count_label = QLabel("No results")
        self.results_count_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        
        # Search time
        self.search_time_label = QLabel("⏱️ Time: --")
        self.search_time_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        
        title_row.addWidget(self.results_title)
        title_row.addStretch()
        title_row.addWidget(self.results_count_label)
        title_row.addWidget(self.search_time_label)
        
        # Progress bar (for search indication)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        
        # Action buttons
        actions_row = QHBoxLayout()
        
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.export_btn.setEnabled(False)
        
        self.clear_results_btn = QPushButton("🗑️ Clear Results")
        self.clear_results_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.clear_results_btn.setEnabled(False)
        
        actions_row.addWidget(self.export_btn)
        actions_row.addWidget(self.clear_results_btn)
        actions_row.addStretch()
        
        header_layout.addLayout(title_row)
        header_layout.addWidget(self.progress_bar)
        header_layout.addLayout(actions_row)
        
        parent_layout.addWidget(header_frame)
    
    def setup_results_content(self, parent_layout: QVBoxLayout) -> None:
        """Set up the scrollable results content area."""
        # Results scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """)
        
        # Scrollable content widget
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(5)
        
        # Empty state label
        self.empty_state_label = QLabel(
            "🔍 No search results yet\n\n"
            "Enter your text and keywords above, then click 'Start Search' to find patterns."
        )
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14pt;
                font-style: italic;
                padding: 40px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 2px dashed #bdc3c7;
            }
        """)
        
        self.scroll_layout.addWidget(self.empty_state_label)
        self.scroll_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        parent_layout.addWidget(self.scroll_area)
        
        # Connect signals
        self.export_btn.clicked.connect(self.export_results)
        self.clear_results_btn.clicked.connect(self.clear_results)
    
    def show_search_progress(self, message: str = "Searching...") -> None:
        """Show search progress indication."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_count_label.setText(message)
        self.search_time_label.setText("⏱️ Time: --")
    
    def hide_search_progress(self) -> None:
        """Hide search progress indication."""
        self.progress_bar.setVisible(False)
    
    def display_results(self, results: List[Dict[str, Any]], search_time: float, search_params: Dict[str, Any]) -> None:
        """Display search results."""
        self.current_results = results
        self.search_time = search_time
        
        # Hide progress
        self.hide_search_progress()
        
        # Clear existing results
        self.clear_results_display()
        
        # Update statistics
        result_count = len(results)
        self.results_count_label.setText(f"📈 Found: {result_count} matches")
        self.search_time_label.setText(f"⏱️ Time: {search_time:.3f}s")
        
        # Enable action buttons
        self.export_btn.setEnabled(result_count > 0)
        self.clear_results_btn.setEnabled(result_count > 0)
        
        if result_count == 0:
            # Show no results message
            no_results_label = QLabel(
                "❌ No matches found\n\n"
                f"Try different keywords or switch to fuzzy search for approximate matches.\n"
                f"Algorithm used: {search_params.get('algorithm', 'Unknown')}"
            )
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 12pt;
                    padding: 30px;
                    background-color: #fdf2f2;
                    border-radius: 8px;
                    border: 2px solid #f1c0c0;
                }
            """)
            self.scroll_layout.addWidget(no_results_label)
        else:
            # Remove empty state
            if self.empty_state_label.parent():
                self.empty_state_label.setParent(None)
            
            # Add result cards
            for i, result in enumerate(results):
                card = ResultCard(result)
                self.scroll_layout.addWidget(card)
                
                # Add click handler
                card.mousePressEvent = lambda event, r=result: self.result_selected.emit(r)
        
        self.scroll_layout.addStretch()
    
    def clear_results_display(self) -> None:
        """Clear the results display area."""
        # Remove all widgets except stretch
        while self.scroll_layout.count() > 0:
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Re-add empty state if no results
        if not self.current_results:
            self.scroll_layout.addWidget(self.empty_state_label)
        
        self.scroll_layout.addStretch()
    
    def clear_results(self) -> None:
        """Clear all results and reset the display."""
        self.current_results = []
        self.search_time = 0.0
        
        # Reset UI
        self.results_count_label.setText("No results")
        self.search_time_label.setText("⏱️ Time: --")
        self.export_btn.setEnabled(False)
        self.clear_results_btn.setEnabled(False)
        
        # Clear display
        self.clear_results_display()
        
        # Show empty state
        if not self.empty_state_label.parent():
            self.scroll_layout.insertWidget(0, self.empty_state_label)
    
    def export_results(self) -> None:
        """Export search results to a file."""
        if not self.current_results:
            return
        
        from PyQt6.QtWidgets import QFileDialog, QMessageBox # type: ignore
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Search Results",
            f"search_results_{int(time.time())}.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'search_time': self.search_time,
                            'result_count': len(self.current_results),
                            'results': self.current_results
                        }, f, indent=2, ensure_ascii=False)
                
                elif file_path.endswith('.csv'):
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
                
                else:  # .txt
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
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported successfully to:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Could not export results:\n{str(e)}"
                )
    
    def get_current_results(self) -> List[Dict[str, Any]]:
        """Get the current search results."""
        return self.current_results.copy()
    
    def get_search_time(self) -> float:
        """Get the last search time."""
        return self.search_time