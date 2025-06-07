from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel # type: ignore
from PyQt6.QtCore import Qt # type: ignore
from PyQt6.QtGui import QFont # type: ignore
from typing import Optional


class HeaderComponent(QWidget):
    """Header component displaying the application name and description."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the header UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 10)
        layout.setSpacing(5)
        
        # App title
        self.title_label = QLabel("String Matching Toolkit")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin: 10px 0;
            }
        """)
        
        # App description
        self.description_label = QLabel("Advanced pattern matching with KMP, Boyer-Moore, Aho-Corasick, and Fuzzy Search")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_font = QFont()
        description_font.setPointSize(11)
        self.description_label.setFont(description_font)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
    
    def set_title(self, title: str) -> None:
        """Set the application title."""
        self.title_label.setText(title)
    
    def set_description(self, description: str) -> None:
        """Set the application description."""
        self.description_label.setText(description)