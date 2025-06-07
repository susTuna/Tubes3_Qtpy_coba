from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QLineEdit, QComboBox, QSpinBox, QPushButton,
                            QFrame, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont # type: ignore
from typing import Optional, List, Dict, Any


class SearchControls(QWidget):
    """Search controls section for keywords, algorithm selection, and search parameters."""
    
    # Signals
    search_requested = pyqtSignal(dict)  # Emitted when search is requested with parameters
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self) -> None:
        """Set up the search controls UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Keywords section
        self.setup_keywords_section(layout)
        
        # Algorithm and parameters section
        self.setup_algorithm_section(layout)
        
        # Search button
        self.setup_search_button(layout)
    
    def setup_keywords_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the keywords input section."""
        # Keywords frame
        keywords_frame = QFrame()
        keywords_frame.setFrameStyle(QFrame.Shape.Box)
        keywords_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
        """)
        
        keywords_layout = QVBoxLayout(keywords_frame)
        keywords_layout.setSpacing(10)
        
        # Keywords header
        keywords_header = QHBoxLayout()
        
        keywords_label = QLabel("🔍 Search Keywords")
        keywords_font = QFont()
        keywords_font.setPointSize(14)
        keywords_font.setBold(True)
        keywords_label.setFont(keywords_font)
        keywords_label.setStyleSheet("color: #2c3e50;")
        
        # Quick add buttons
        quick_add_layout = QHBoxLayout()
        
        self.add_keyword_btn = QPushButton("+ Add")
        self.add_keyword_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        
        self.clear_keywords_btn = QPushButton("Clear All")
        self.clear_keywords_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        quick_add_layout.addWidget(self.add_keyword_btn)
        quick_add_layout.addWidget(self.clear_keywords_btn)
        quick_add_layout.addStretch()
        
        keywords_header.addWidget(keywords_label)
        keywords_header.addStretch()
        keywords_header.addLayout(quick_add_layout)
        
        # Keywords input
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Enter keywords separated by commas (e.g., python, algorithm, search)")
        self.keywords_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Keywords display area
        keywords_display_label = QLabel("Keywords to search:")
        keywords_display_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        
        # Scrollable keywords display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(80)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.keywords_display = QTextEdit()
        self.keywords_display.setReadOnly(True)
        self.keywords_display.setMaximumHeight(60)
        self.keywords_display.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                color: #2c3e50;
                font-family: monospace;
            }
        """)
        scroll_area.setWidget(self.keywords_display)
        
        keywords_layout.addLayout(keywords_header)
        keywords_layout.addWidget(self.keywords_input)
        keywords_layout.addWidget(keywords_display_label)
        keywords_layout.addWidget(scroll_area)
        
        parent_layout.addWidget(keywords_frame)
    
    def setup_algorithm_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the algorithm selection and parameters section."""
        # Algorithm frame
        algorithm_frame = QFrame()
        algorithm_frame.setFrameStyle(QFrame.Shape.Box)
        algorithm_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
        """)
        
        algorithm_layout = QVBoxLayout(algorithm_frame)
        algorithm_layout.setSpacing(15)
        
        # Algorithm header
        algorithm_label = QLabel("⚙️ Search Algorithm & Parameters")
        algorithm_font = QFont()
        algorithm_font.setPointSize(14)
        algorithm_font.setBold(True)
        algorithm_label.setFont(algorithm_font)
        algorithm_label.setStyleSheet("color: #2c3e50;")
        
        # Algorithm selection row
        algo_row = QHBoxLayout()
        
        algo_select_label = QLabel("Algorithm:")
        algo_select_label.setMinimumWidth(120)
        algo_select_label.setStyleSheet("font-weight: bold; color: #34495e;")
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "KMP (Knuth-Morris-Pratt)",
            "Boyer-Moore Simple",
            "Boyer-Moore Complex", 
            "Aho-Corasick",
            "Fuzzy Search"
        ])
        self.algorithm_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        algo_row.addWidget(algo_select_label)
        algo_row.addWidget(self.algorithm_combo)
        algo_row.addStretch()
        
        # Parameters row
        params_row = QHBoxLayout()
        
        # Top matches count
        matches_label = QLabel("Top Matches:")
        matches_label.setMinimumWidth(120)
        matches_label.setStyleSheet("font-weight: bold; color: #34495e;")
        
        self.top_matches_spin = QSpinBox()
        self.top_matches_spin.setRange(1, 1000)
        self.top_matches_spin.setValue(10)
        self.top_matches_spin.setSuffix(" results")
        self.top_matches_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
                min-width: 120px;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Case sensitive option (for exact matches)
        case_label = QLabel("Case Sensitive:")
        case_label.setMinimumWidth(120)
        case_label.setStyleSheet("font-weight: bold; color: #34495e;")
        
        self.case_sensitive_combo = QComboBox()
        self.case_sensitive_combo.addItems(["No", "Yes"])
        self.case_sensitive_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
                min-width: 80px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        params_row.addWidget(matches_label)
        params_row.addWidget(self.top_matches_spin)
        params_row.addWidget(case_label)
        params_row.addWidget(self.case_sensitive_combo)
        params_row.addStretch()
        
        # Algorithm info
        self.algorithm_info = QLabel("ℹ️ KMP: Efficient for single pattern matching with linear time complexity")
        self.algorithm_info.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.algorithm_info.setWordWrap(True)
        
        algorithm_layout.addWidget(algorithm_label)
        algorithm_layout.addLayout(algo_row)
        algorithm_layout.addLayout(params_row)
        algorithm_layout.addWidget(self.algorithm_info)
        
        parent_layout.addWidget(algorithm_frame)
    
    def setup_search_button(self, parent_layout: QVBoxLayout) -> None:
        """Set up the search button."""
        button_layout = QHBoxLayout()
        
        self.search_btn = QPushButton("🔍 Start Search")
        self.search_btn.setMinimumHeight(50)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.search_btn)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.add_keyword_btn.clicked.connect(self.add_keyword)
        self.clear_keywords_btn.clicked.connect(self.clear_keywords)
        self.keywords_input.returnPressed.connect(self.add_keyword)
        self.algorithm_combo.currentTextChanged.connect(self.update_algorithm_info)
        self.search_btn.clicked.connect(self.request_search)
    
    def add_keyword(self) -> None:
        """Add keyword(s) from the input field."""
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            return
        
        # Split by commas and clean up
        new_keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
        
        if new_keywords:
            current_keywords = self.get_keywords()
            # Add only unique keywords
            for keyword in new_keywords:
                if keyword not in current_keywords:
                    current_keywords.append(keyword)
            
            self.update_keywords_display(current_keywords)
            self.keywords_input.clear()
    
    def clear_keywords(self) -> None:
        """Clear all keywords."""
        self.keywords_display.clear()
    
    def update_keywords_display(self, keywords: List[str]) -> None:
        """Update the keywords display area."""
        if keywords:
            display_text = ", ".join(f'"{kw}"' for kw in keywords)
            self.keywords_display.setPlainText(display_text)
        else:
            self.keywords_display.clear()
    
    def get_keywords(self) -> List[str]:
        """Get the current list of keywords."""
        text = self.keywords_display.toPlainText()
        if not text:
            return []
        
        # Extract keywords from quotes
        keywords = []
        import re
        matches = re.findall(r'"([^"]*)"', text)
        return matches
    
    def update_algorithm_info(self, algorithm: str) -> None:
        """Update algorithm information display."""
        info_map = {
            "KMP (Knuth-Morris-Pratt)": "ℹ️ KMP: Efficient for single pattern matching with linear time complexity O(n+m)",
            "Boyer-Moore Simple": "ℹ️ Boyer-Moore Simple: Uses bad character heuristic for fast pattern matching",
            "Boyer-Moore Complex": "ℹ️ Boyer-Moore Complex: Uses both bad character and good suffix heuristics for optimal performance",
            "Aho-Corasick": "ℹ️ Aho-Corasick: Optimal for multiple pattern matching, finds all patterns simultaneously",
            "Fuzzy Search": "ℹ️ Fuzzy Search: Finds approximate matches using edit distance, great for typos and variations"
        }
        
        self.algorithm_info.setText(info_map.get(algorithm, "ℹ️ Select an algorithm to see information"))
    
    def request_search(self) -> None:
        """Request search with current parameters."""
        keywords = self.get_keywords()
        
        if not keywords:
            from PyQt6.QtWidgets import QMessageBox # type: ignore
            QMessageBox.warning(
                self,
                "No Keywords",
                "Please add at least one keyword to search for."
            )
            return
        
        # Prepare search parameters
        search_params = {
            'keywords': keywords,
            'algorithm': self.algorithm_combo.currentText(),
            'top_matches': self.top_matches_spin.value(),
            'case_sensitive': self.case_sensitive_combo.currentText() == "Yes"
        }
        
        self.search_requested.emit(search_params)
    
    def set_search_enabled(self, enabled: bool) -> None:
        """Enable or disable the search button."""
        self.search_btn.setEnabled(enabled)
        if not enabled:
            self.search_btn.setText("🔄 Searching...")
        else:
            self.search_btn.setText("🔍 Start Search")
    
    def get_search_parameters(self) -> Dict[str, Any]:
        """Get current search parameters."""
        return {
            'keywords': self.get_keywords(),
            'algorithm': self.algorithm_combo.currentText(),
            'top_matches': self.top_matches_spin.value(),
            'case_sensitive': self.case_sensitive_combo.currentText() == "Yes"
        }