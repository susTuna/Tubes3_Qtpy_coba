from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QTextEdit, QPushButton, QFileDialog, QMessageBox,
                            QFrame)
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont, QIcon # type: ignore
from typing import Optional
import os


class InputSection(QWidget):
    """Input section for text input and file loading."""
    
    # Signals
    text_changed = pyqtSignal(str)  # Emitted when text content changes
    file_loaded = pyqtSignal(str, str)  # Emitted when file is loaded (filename, content)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_file_path: Optional[str] = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self) -> None:
        """Set up the input section UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        
        # Section frame
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.Box)
        self.frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(10)
        
        # Section header
        header_layout = QHBoxLayout()
        
        self.section_label = QLabel("📄 Input Text")
        section_font = QFont()
        section_font.setPointSize(14)
        section_font.setBold(True)
        self.section_label.setFont(section_font)
        self.section_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        # File controls
        file_controls_layout = QHBoxLayout()
        
        self.load_file_btn = QPushButton("📁 Load File")
        self.load_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        file_controls_layout.addWidget(self.load_file_btn)
        file_controls_layout.addWidget(self.clear_btn)
        file_controls_layout.addStretch()
        
        header_layout.addWidget(self.section_label)
        header_layout.addStretch()
        header_layout.addLayout(file_controls_layout)
        
        # File info label
        self.file_info_label = QLabel("Type or paste your text below, or load from a file")
        self.file_info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        # Text input area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter your text here...\n\n"
            "You can type directly or load a text file using the 'Load File' button above.\n"
            "Supported formats: .txt, .md, .py, .js, .html, .css, .json, .xml"
        )
        self.text_input.setMinimumHeight(200)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Character count label
        self.char_count_label = QLabel("Characters: 0")
        self.char_count_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Add components to frame layout
        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(self.file_info_label)
        frame_layout.addWidget(self.text_input)
        frame_layout.addWidget(self.char_count_label)
        
        layout.addWidget(self.frame)
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.load_file_btn.clicked.connect(self.load_file)
        self.clear_btn.clicked.connect(self.clear_text)
        self.text_input.textChanged.connect(self.on_text_changed)
    
    def load_file(self) -> None:
        """Load text from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Text File",
            "",
            "Text Files (*.txt *.md *.py *.js *.html *.css *.json *.xml);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.text_input.setPlainText(content)
                self.current_file_path = file_path
                filename = os.path.basename(file_path)
                self.file_info_label.setText(f"📁 Loaded: {filename} ({len(content):,} characters)")
                self.file_info_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                
                self.file_loaded.emit(filename, content)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "File Load Error",
                    f"Could not load file: {str(e)}"
                )
    
    def clear_text(self) -> None:
        """Clear the text input."""
        self.text_input.clear()
        self.current_file_path = None
        self.file_info_label.setText("Type or paste your text below, or load from a file")
        self.file_info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
    
    def on_text_changed(self) -> None:
        """Handle text change events."""
        text = self.text_input.toPlainText()
        char_count = len(text)
        
        # Update character count
        self.char_count_label.setText(f"Characters: {char_count:,}")
        
        # Update file info if text was modified
        if self.current_file_path and text:
            filename = os.path.basename(self.current_file_path)
            self.file_info_label.setText(f"📁 {filename} (modified) - {char_count:,} characters")
            self.file_info_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        elif not text:
            self.file_info_label.setText("Type or paste your text below, or load from a file")
            self.file_info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        # Emit signal
        self.text_changed.emit(text)
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.text_input.toPlainText()
    
    def set_text(self, text: str) -> None:
        """Set the text content."""
        self.text_input.setPlainText(text)
    
    def get_file_path(self) -> Optional[str]:
        """Get the current file path."""
        return self.current_file_path