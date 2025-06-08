from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QLineEdit, QComboBox, QSpinBox, QPushButton,
                            QFrame, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont # type: ignore
from typing import Optional, List, Dict, Any
from .general_config import gui_config, SearchConfig


class ConfigurableSearchControls(QWidget):
    """Highly configurable search controls section for keywords, algorithm selection, and search parameters."""
    
    # Signals
    search_requested = pyqtSignal(dict)  # Emitted when search is requested with parameters
    keyword_added = pyqtSignal(str)  # Emitted when a keyword is added
    keywords_cleared = pyqtSignal()  # Emitted when keywords are cleared
    algorithm_changed = pyqtSignal(str)  # Emitted when algorithm selection changes
    
    def __init__(self, 
                 config: Optional[SearchConfig] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Configuration
        self.config = config or gui_config.search
        self.gui_config = gui_config
        
        # UI Elements
        self.keywords_input: Optional[QLineEdit] = None
        self.keywords_display: Optional[QTextEdit] = None
        self.add_keyword_btn: Optional[QPushButton] = None
        self.clear_keywords_btn: Optional[QPushButton] = None
        self.algorithm_combo: Optional[QComboBox] = None
        self.algorithm_info: Optional[QLabel] = None
        self.top_matches_spin: Optional[QSpinBox] = None
        self.case_sensitive_combo: Optional[QComboBox] = None
        self.search_btn: Optional[QPushButton] = None
        
        self.setup_ui()
        self.connect_signals()
        self.apply_styling()
    
    def setup_ui(self) -> None:
        """Set up the search controls UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_medium
        )
        layout.setSpacing(self.gui_config.spacing.margin_large)
        
        # Keywords section
        if self.config.show_keywords_section:
            self.setup_keywords_section(layout)
        
        # Algorithm and parameters section
        if self.config.show_algorithm_section:
            self.setup_algorithm_section(layout)
        
        # Search button
        self.setup_search_button(layout)
    
    def setup_keywords_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the keywords input section."""
        # Keywords frame
        keywords_frame = QFrame()
        keywords_frame.setObjectName("keywordsFrame")
        keywords_frame.setFrameStyle(QFrame.Shape.Box)
        
        keywords_layout = QVBoxLayout(keywords_frame)
        keywords_layout.setSpacing(self.gui_config.spacing.margin_medium)
        keywords_layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium
        )
        
        # Keywords header
        keywords_header = QHBoxLayout()
        
        keywords_label = QLabel("🔍 Search Keywords")
        keywords_label.setObjectName("keywordsTitle")
        
        keywords_font = QFont(self.gui_config.fonts.family_primary)
        keywords_font.setPointSize(self.gui_config.fonts.size_large)
        keywords_font.setWeight(QFont.Weight(self.gui_config.fonts.weight_bold))
        keywords_label.setFont(keywords_font)
        
        keywords_header.addWidget(keywords_label)
        keywords_header.addStretch()
        
        # Quick add buttons
        if self.config.show_quick_add_buttons:
            self.setup_quick_add_buttons(keywords_header)
        
        # Keywords input
        self.keywords_input = QLineEdit()
        self.keywords_input.setObjectName("keywordsInput")
        self.keywords_input.setPlaceholderText(self.config.keywords_placeholder)
        
        # Keywords display area
        keywords_display_label = QLabel("Keywords to search:")
        keywords_display_label.setObjectName("keywordsDisplayLabel")
        
        # Scrollable keywords display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(self.config.max_keywords_display_height)
        scroll_area.setObjectName("keywordsScrollArea")
        
        self.keywords_display = QTextEdit()
        self.keywords_display.setObjectName("keywordsDisplay")
        self.keywords_display.setReadOnly(True)
        self.keywords_display.setMaximumHeight(self.config.max_keywords_display_height - 20)
        scroll_area.setWidget(self.keywords_display)
        
        keywords_layout.addLayout(keywords_header)
        keywords_layout.addWidget(self.keywords_input)
        keywords_layout.addWidget(keywords_display_label)
        keywords_layout.addWidget(scroll_area)
        
        parent_layout.addWidget(keywords_frame)
    
    def setup_quick_add_buttons(self, layout: QHBoxLayout) -> None:
        """Set up quick add buttons for keywords."""
        quick_add_layout = QHBoxLayout()
        
        self.add_keyword_btn = QPushButton(self.config.add_keyword_text)
        self.add_keyword_btn.setObjectName("addKeywordBtn")
        
        self.clear_keywords_btn = QPushButton(self.config.clear_keywords_text)
        self.clear_keywords_btn.setObjectName("clearKeywordsBtn")
        
        quick_add_layout.addWidget(self.add_keyword_btn)
        quick_add_layout.addWidget(self.clear_keywords_btn)
        quick_add_layout.addStretch()
        
        layout.addLayout(quick_add_layout)
    
    def setup_algorithm_section(self, parent_layout: QVBoxLayout) -> None:
        """Set up the algorithm selection and parameters section."""
        # Algorithm frame
        algorithm_frame = QFrame()
        algorithm_frame.setObjectName("algorithmFrame")
        algorithm_frame.setFrameStyle(QFrame.Shape.Box)
        
        algorithm_layout = QVBoxLayout(algorithm_frame)
        algorithm_layout.setSpacing(self.gui_config.spacing.margin_large)
        algorithm_layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium
        )
        
        # Algorithm header
        algorithm_label = QLabel("⚙️ Search Algorithm & Parameters")
        algorithm_label.setObjectName("algorithmTitle")
        
        algorithm_font = QFont(self.gui_config.fonts.family_primary)
        algorithm_font.setPointSize(self.gui_config.fonts.size_large)
        algorithm_font.setWeight(QFont.Weight(self.gui_config.fonts.weight_bold))
        algorithm_label.setFont(algorithm_font)
        
        # Algorithm selection row
        algo_row = QHBoxLayout()
        
        algo_select_label = QLabel("Algorithm:")
        algo_select_label.setObjectName("algorithmSelectLabel")
        algo_select_label.setMinimumWidth(120)
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setObjectName("algorithmCombo")
        self.algorithm_combo.addItems(list(self.config.available_algorithms))
        
        # Set default algorithm
        default_index = list(self.config.available_algorithms).index(self.config.default_algorithm)
        self.algorithm_combo.setCurrentIndex(default_index)
        
        algo_row.addWidget(algo_select_label)
        algo_row.addWidget(self.algorithm_combo)
        algo_row.addStretch()
        
        # Parameters row
        if self.config.show_search_parameters:
            params_row = self.setup_search_parameters()
        
        # Algorithm info
        if self.config.show_algorithm_info:
            self.algorithm_info = QLabel()
            self.algorithm_info.setObjectName("algorithmInfo")
            self.algorithm_info.setWordWrap(True)
            self.update_algorithm_info(self.config.default_algorithm)
        
        algorithm_layout.addWidget(algorithm_label)
        algorithm_layout.addLayout(algo_row)
        
        if self.config.show_search_parameters:
            algorithm_layout.addLayout(params_row)
        
        if self.config.show_algorithm_info:
            algorithm_layout.addWidget(self.algorithm_info)
        
        parent_layout.addWidget(algorithm_frame)
    
    def setup_search_parameters(self) -> QHBoxLayout:
        """Set up search parameters controls."""
        params_row = QHBoxLayout()
        
        # Top matches count
        matches_label = QLabel("Top Matches:")
        matches_label.setObjectName("matchesLabel")
        matches_label.setMinimumWidth(120)
        
        self.top_matches_spin = QSpinBox()
        self.top_matches_spin.setObjectName("topMatchesSpin")
        self.top_matches_spin.setRange(1, self.config.max_top_matches)
        self.top_matches_spin.setValue(self.config.default_top_matches)
        self.top_matches_spin.setSuffix(" results")
        
        # Case sensitive option
        case_label = QLabel("Case Sensitive:")
        case_label.setObjectName("caseLabel")
        case_label.setMinimumWidth(120)
        
        self.case_sensitive_combo = QComboBox()
        self.case_sensitive_combo.setObjectName("caseSensitiveCombo")
        self.case_sensitive_combo.addItems(["No", "Yes"])
        
        if self.config.default_case_sensitive:
            self.case_sensitive_combo.setCurrentText("Yes")
        
        params_row.addWidget(matches_label)
        params_row.addWidget(self.top_matches_spin)
        params_row.addWidget(case_label)
        params_row.addWidget(self.case_sensitive_combo)
        params_row.addStretch()
        
        return params_row
    
    def setup_search_button(self, parent_layout: QVBoxLayout) -> None:
        """Set up the search button."""
        button_layout = QHBoxLayout()
        
        self.search_btn = QPushButton(self.config.search_button_text)
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.setMinimumHeight(50)
        
        button_layout.addStretch()
        button_layout.addWidget(self.search_btn)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def apply_styling(self) -> None:
        """Apply CSS styling to all components."""
        # Frame styles
        frame_style = f"""
        QFrame#keywordsFrame, QFrame#algorithmFrame {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
            padding: {self.gui_config.spacing.padding_medium}px;
        }}
        """
        
        # Title styles
        title_style = f"""
        QLabel#keywordsTitle, QLabel#algorithmTitle {{
            color: {self.gui_config.colors.text_primary};
            margin-bottom: {self.gui_config.spacing.margin_small}px;
        }}
        """
        
        # Input styles
        input_style = f"""
        QLineEdit#keywordsInput {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_medium}px;
            font-size: {self.gui_config.fonts.size_normal}pt;
        }}
        QLineEdit#keywordsInput:focus {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.secondary};
        }}
        """
        
        # Button styles
        button_style = f"""
        QPushButton#addKeywordBtn {{
            background-color: {self.gui_config.colors.success};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#addKeywordBtn:hover {{
            background-color: {self.gui_config.colors.primary};
        }}
        
        QPushButton#clearKeywordsBtn {{
            background-color: {self.gui_config.colors.danger};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#clearKeywordsBtn:hover {{
            background-color: {self.gui_config.colors.accent};
        }}
        
        QPushButton#searchBtn {{
            background-color: {self.gui_config.colors.success};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            font-size: {self.gui_config.fonts.size_xlarge}pt;
            font-weight: bold;
            padding: {self.gui_config.spacing.padding_medium}px {self.gui_config.spacing.padding_large}px;
        }}
        QPushButton#searchBtn:hover {{
            background-color: {self.gui_config.colors.primary};
        }}
        QPushButton#searchBtn:pressed {{
            background-color: {self.gui_config.colors.text_primary};
        }}
        QPushButton#searchBtn:disabled {{
            background-color: {self.gui_config.colors.border_medium};
            color: {self.gui_config.colors.text_secondary};
        }}
        """
        
        # ComboBox and SpinBox styles
        control_style = f"""
        QComboBox#algorithmCombo, QComboBox#caseSensitiveCombo {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_medium}px;
            font-size: {self.gui_config.fonts.size_normal}pt;
            min-width: 120px;
        }}
        QComboBox#algorithmCombo:focus, QComboBox#caseSensitiveCombo:focus {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.secondary};
        }}
        
        QSpinBox#topMatchesSpin {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_medium}px;
            font-size: {self.gui_config.fonts.size_normal}pt;
            min-width: 120px;
        }}
        QSpinBox#topMatchesSpin:focus {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.secondary};
        }}
        """
        
        # Text display styles
        display_style = f"""
        QTextEdit#keywordsDisplay {{
            border: none;
            background-color: transparent;
            color: {self.gui_config.colors.text_primary};
            font-family: {self.gui_config.fonts.family_monospace};
        }}
        
        QScrollArea#keywordsScrollArea {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            background-color: {self.gui_config.colors.bg_secondary};
        }}
        
        QLabel#keywordsDisplayLabel, QLabel#algorithmSelectLabel, QLabel#matchesLabel, QLabel#caseLabel {{
            color: {self.gui_config.colors.text_secondary};
            font-weight: bold;
        }}
        
        QLabel#algorithmInfo {{
            color: {self.gui_config.colors.text_secondary};
            font-style: italic;
            background-color: {self.gui_config.colors.bg_secondary};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_medium}px;
        }}
        """
        
        # Combine all styles
        full_style = frame_style + title_style + input_style + button_style + control_style + display_style
        
        # Apply custom styles if provided
        if self.config.custom_frame_style:
            full_style += f"QFrame {{ {self.config.custom_frame_style} }}"
        
        if self.config.custom_button_style:
            full_style += f"QPushButton {{ {self.config.custom_button_style} }}"
        
        if self.config.custom_input_style:
            full_style += f"QLineEdit, QComboBox, QSpinBox {{ {self.config.custom_input_style} }}"
        
        self.setStyleSheet(full_style)
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        if self.add_keyword_btn:
            self.add_keyword_btn.clicked.connect(self.add_keyword)
        if self.clear_keywords_btn:
            self.clear_keywords_btn.clicked.connect(self.clear_keywords)
        if self.keywords_input:
            self.keywords_input.returnPressed.connect(self.add_keyword)
        if self.algorithm_combo:
            self.algorithm_combo.currentTextChanged.connect(self.update_algorithm_info)
            self.algorithm_combo.currentTextChanged.connect(self.algorithm_changed.emit)
        if self.search_btn:
            self.search_btn.clicked.connect(self.request_search)
    
    def add_keyword(self) -> None:
        """Add keyword(s) from the input field."""
        if not self.keywords_input:
            return
            
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
                    self.keyword_added.emit(keyword)
            
            self.update_keywords_display(current_keywords)
            self.keywords_input.clear()
    
    def clear_keywords(self) -> None:
        """Clear all keywords."""
        if self.keywords_display:
            self.keywords_display.clear()
        self.keywords_cleared.emit()
    
    def update_keywords_display(self, keywords: List[str]) -> None:
        """Update the keywords display area."""
        if not self.keywords_display:
            return
            
        if keywords:
            display_text = ", ".join(f'"{kw}"' for kw in keywords)
            self.keywords_display.setPlainText(display_text)
        else:
            self.keywords_display.clear()
    
    def get_keywords(self) -> List[str]:
        """Get the current list of keywords."""
        if not self.keywords_display:
            return []
            
        text = self.keywords_display.toPlainText()
        if not text:
            return []
        
        # Extract keywords from quotes
        import re
        matches = re.findall(r'"([^"]*)"', text)
        return matches
    
    def update_algorithm_info(self, algorithm: str) -> None:
        """Update algorithm information display."""
        if not self.algorithm_info:
            return
            
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
            'algorithm': self.algorithm_combo.currentText() if self.algorithm_combo else self.config.default_algorithm,
            'top_matches': self.top_matches_spin.value() if self.top_matches_spin else self.config.default_top_matches,
            'case_sensitive': (self.case_sensitive_combo.currentText() == "Yes") if self.case_sensitive_combo else self.config.default_case_sensitive
        }
        
        self.search_requested.emit(search_params)
    
    def set_search_enabled(self, enabled: bool) -> None:
        """Enable or disable the search button."""
        if not self.search_btn:
            return
            
        self.search_btn.setEnabled(enabled)
        if not enabled:
            self.search_btn.setText(self.config.searching_button_text)
        else:
            self.search_btn.setText(self.config.search_button_text)
    
    def get_search_parameters(self) -> Dict[str, Any]:
        """Get current search parameters."""
        return {
            'keywords': self.get_keywords(),
            'algorithm': self.algorithm_combo.currentText() if self.algorithm_combo else self.config.default_algorithm,
            'top_matches': self.top_matches_spin.value() if self.top_matches_spin else self.config.default_top_matches,
            'case_sensitive': (self.case_sensitive_combo.currentText() == "Yes") if self.case_sensitive_combo else self.config.default_case_sensitive
        }
    
    def set_keywords(self, keywords: List[str]) -> None:
        """Set keywords programmatically."""
        self.update_keywords_display(keywords)
    
    def set_algorithm(self, algorithm: str) -> None:
        """Set the selected algorithm."""
        if self.algorithm_combo and algorithm in self.config.available_algorithms:
            self.algorithm_combo.setCurrentText(algorithm)
    
    def update_config(self, config: SearchConfig) -> None:
        """Update search configuration and refresh UI."""
        self.config = config
        self.setup_ui()
        self.apply_styling()
    
    def set_theme(self, theme_name: str) -> None:
        """Apply a different theme to the search section."""
        self.gui_config.set_theme(theme_name)
        self.apply_styling()


# Backward compatibility - keep your original simple search controls
class SearchControls(ConfigurableSearchControls):
    """Simple search controls for backward compatibility."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)