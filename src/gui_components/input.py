from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QTextEdit, QPushButton, QFileDialog, QMessageBox,
                            QFrame, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont, QIcon # type: ignore
from typing import Optional, List
from .general_config import gui_config, InputConfig
import os


class ConfigurableInputSection(QWidget):
    """Highly configurable input section for text input and file loading."""
    
    # Signals
    text_changed = pyqtSignal(str)  # Emitted when text content changes
    file_loaded = pyqtSignal(str, str)  # Emitted when file is loaded (filename, content)
    file_load_started = pyqtSignal()  # Emitted when file loading starts
    file_load_finished = pyqtSignal()  # Emitted when file loading finishes
    clear_requested = pyqtSignal()  # Emitted when clear is requested
    
    def __init__(self, 
                 title: str = "📄 Input Text",
                 config: Optional[InputConfig] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Configuration
        self.config = config or gui_config.input
        self.gui_config = gui_config
        
        # Content
        self._title = title
        self.current_file_path: Optional[str] = None
        
        # UI Elements
        self.frame: Optional[QFrame] = None
        self.section_label: Optional[QLabel] = None
        self.load_file_btn: Optional[QPushButton] = None
        self.clear_btn: Optional[QPushButton] = None
        self.file_info_label: Optional[QLabel] = None
        self.text_input: Optional[QTextEdit] = None
        self.char_count_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        
        self.setup_ui()
        self.connect_signals()
        self.apply_styling()
    
    def setup_ui(self) -> None:
        """Set up the input section UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_medium
        )
        layout.setSpacing(self.gui_config.spacing.margin_medium)
        
        # Section frame
        self.frame = QFrame()
        self.frame.setObjectName("inputFrame")
        self.frame.setFrameStyle(QFrame.Shape.Box)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(self.gui_config.spacing.margin_medium)
        frame_layout.setContentsMargins(
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium,
            self.gui_config.spacing.margin_medium
        )
        
        # Section header
        self.setup_header(frame_layout)
        
        # File info label
        if self.config.show_file_info:
            self.setup_file_info(frame_layout)
        
        # Text input area
        self.setup_text_input(frame_layout)
        
        # Character count and progress
        self.setup_footer(frame_layout)
        
        layout.addWidget(self.frame)
    
    def setup_header(self, layout: QVBoxLayout) -> None:
        """Set up the header section with title and controls."""
        header_layout = QHBoxLayout()
        
        # Section title
        self.section_label = QLabel(self._title)
        self.section_label.setObjectName("inputTitle")
        
        title_font = QFont(self.gui_config.fonts.family_primary)
        title_font.setPointSize(self.gui_config.fonts.size_large)
        title_font.setWeight(QFont.Weight(self.gui_config.fonts.weight_bold))
        self.section_label.setFont(title_font)
        
        header_layout.addWidget(self.section_label)
        header_layout.addStretch()
        
        # File controls
        if self.config.show_file_controls:
            self.setup_file_controls(header_layout)
        
        layout.addLayout(header_layout)
    
    def setup_file_controls(self, layout: QHBoxLayout) -> None:
        """Set up file control buttons."""
        file_controls_layout = QHBoxLayout()
        
        if self.config.show_load_button:
            self.load_file_btn = QPushButton(self.config.load_button_text)
            self.load_file_btn.setObjectName("loadButton")
            file_controls_layout.addWidget(self.load_file_btn)
        
        if self.config.show_clear_button:
            self.clear_btn = QPushButton(self.config.clear_button_text)
            self.clear_btn.setObjectName("clearButton")
            file_controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(file_controls_layout)
    
    def setup_file_info(self, layout: QVBoxLayout) -> None:
        """Set up file information label."""
        self.file_info_label = QLabel("Type or paste your text below, or load from a file")
        self.file_info_label.setObjectName("fileInfo")
        layout.addWidget(self.file_info_label)
    
    def setup_text_input(self, layout: QVBoxLayout) -> None:
        """Set up the text input area."""
        self.text_input = QTextEdit()
        self.text_input.setObjectName("textInput")
        
        # Configure text area
        self.text_input.setPlaceholderText(self._build_placeholder_text())
        self.text_input.setMinimumHeight(self.config.min_height)
        self.text_input.setMaximumHeight(self.config.max_height)
        
        # Font configuration
        text_font = QFont(self.config.font_family)
        text_font.setPointSize(self.config.font_size)
        self.text_input.setFont(text_font)
        
        # Word wrap
        if self.config.word_wrap:
            self.text_input.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.text_input.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        layout.addWidget(self.text_input)
    
    def setup_footer(self, layout: QVBoxLayout) -> None:
        """Set up footer with character count and progress bar."""
        footer_layout = QHBoxLayout()
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(5)
        
        # Character count
        if self.config.show_character_count:
            self.char_count_label = QLabel("Characters: 0")
            self.char_count_label.setObjectName("charCount")
            
            count_font = QFont(self.gui_config.fonts.family_primary)
            count_font.setPointSize(self.gui_config.fonts.size_small)
            self.char_count_label.setFont(count_font)
            self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            footer_layout.addStretch()
            footer_layout.addWidget(self.char_count_label)
        
        layout.addWidget(self.progress_bar)
        layout.addLayout(footer_layout)
    
    def _build_placeholder_text(self) -> str:
        """Build placeholder text based on configuration."""
        base_text = self.config.placeholder_text + "\n\n"
        
        if self.config.show_file_controls:
            base_text += "You can type directly or load a text file using the 'Load File' button above.\n"
        
        # Add supported extensions info
        extensions = self.config.supported_extensions.split(';;')[0]
        extensions = extensions.replace('Text Files (', '').replace(')', '')
        base_text += f"Supported formats: {extensions}"
        
        return base_text
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        if self.load_file_btn:
            self.load_file_btn.clicked.connect(self.load_file)
        if self.clear_btn:
            self.clear_btn.clicked.connect(self.clear_text)
        if self.text_input:
            self.text_input.textChanged.connect(self.on_text_changed)
    
    def apply_styling(self) -> None:
        """Apply CSS styling to all components."""
        # Frame style
        frame_style = f"""
        QFrame#inputFrame {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_large}px;
            background-color: {self.gui_config.colors.bg_primary};
            padding: {self.gui_config.spacing.padding_medium}px;
        }}
        """
        
        # Title style
        title_style = f"""
        QLabel#inputTitle {{
            color: {self.gui_config.colors.text_primary};
            margin-bottom: {self.gui_config.spacing.margin_small}px;
        }}
        """
        
        # Button styles
        load_button_style = f"""
        QPushButton#loadButton {{
            background-color: {self.gui_config.colors.secondary};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#loadButton:hover {{
            background-color: {self.gui_config.colors.primary};
        }}
        QPushButton#loadButton:pressed {{
            background-color: {self.gui_config.colors.text_primary};
        }}
        """
        
        clear_button_style = f"""
        QPushButton#clearButton {{
            background-color: {self.gui_config.colors.danger};
            color: {self.gui_config.colors.text_light};
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_small}px {self.gui_config.spacing.padding_medium}px;
            font-weight: bold;
        }}
        QPushButton#clearButton:hover {{
            background-color: {self.gui_config.colors.accent};
        }}
        """
        
        # Text input style
        text_input_style = f"""
        QTextEdit#textInput {{
            border: {self.gui_config.spacing.border_width_thin}px solid {self.gui_config.colors.border_medium};
            border-radius: {self.gui_config.spacing.border_radius_medium}px;
            padding: {self.gui_config.spacing.padding_medium}px;
            background-color: {self.gui_config.colors.bg_primary};
            color: {self.gui_config.colors.text_primary};
            line-height: {self.config.line_height};
        }}
        QTextEdit#textInput:focus {{
            border: {self.gui_config.spacing.border_width_medium}px solid {self.gui_config.colors.secondary};
        }}
        """
        
        # File info style
        file_info_style = f"""
        QLabel#fileInfo {{
            color: {self.gui_config.colors.text_secondary};
            font-style: italic;
        }}
        """
        
        # Character count style
        char_count_style = f"""
        QLabel#charCount {{
            color: {self.gui_config.colors.text_secondary};
        }}
        """
        
        # Progress bar style
        progress_style = f"""
        QProgressBar#progressBar {{
            border: none;
            border-radius: {self.gui_config.spacing.border_radius_small}px;
            background-color: {self.gui_config.colors.border_light};
        }}
        QProgressBar#progressBar::chunk {{
            background-color: {self.gui_config.colors.secondary};
            border-radius: {self.gui_config.spacing.border_radius_small}px;
        }}
        """
        
        # Combine all styles
        full_style = (frame_style + title_style + load_button_style + 
                     clear_button_style + text_input_style + file_info_style + 
                     char_count_style + progress_style)
        
        # Apply custom styles if provided
        if self.config.custom_frame_style:
            full_style += f"QFrame#inputFrame {{ {self.config.custom_frame_style} }}"
        
        if self.config.custom_textarea_style:
            full_style += f"QTextEdit#textInput {{ {self.config.custom_textarea_style} }}"
        
        if self.config.custom_button_style:
            full_style += f"QPushButton {{ {self.config.custom_button_style} }}"
        
        self.setStyleSheet(full_style)
    
    def load_file(self) -> None:
        """Load text from a file with progress indication."""
        self.file_load_started.emit()
        
        if self.progress_bar:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Text File",
            self.config.default_directory,
            self.config.supported_extensions
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.text_input.setPlainText(content)
                self.current_file_path = file_path
                filename = os.path.basename(file_path)
                
                if self.file_info_label:
                    self.file_info_label.setText(f"📁 Loaded: {filename} ({len(content):,} characters)")
                    self.file_info_label.setStyleSheet(f"color: {self.gui_config.colors.success}; font-weight: bold;")
                
                self.file_loaded.emit(filename, content)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "File Load Error",
                    f"Could not load file: {str(e)}"
                )
        
        if self.progress_bar:
            self.progress_bar.setVisible(False)
        
        self.file_load_finished.emit()
    
    def clear_text(self) -> None:
        """Clear the text input."""
        self.clear_requested.emit()
        
        if self.text_input:
            self.text_input.clear()
        
        self.current_file_path = None
        
        if self.file_info_label:
            self.file_info_label.setText("Type or paste your text below, or load from a file")
            self.file_info_label.setStyleSheet(f"color: {self.gui_config.colors.text_secondary}; font-style: italic;")
    
    def on_text_changed(self) -> None:
        """Handle text change events."""
        if not self.text_input:
            return
            
        text = self.text_input.toPlainText()
        char_count = len(text)
        
        # Update character count
        if self.char_count_label:
            self.char_count_label.setText(f"Characters: {char_count:,}")
        
        # Update file info if text was modified
        if self.file_info_label:
            if self.current_file_path and text:
                filename = os.path.basename(self.current_file_path)
                self.file_info_label.setText(f"📁 {filename} (modified) - {char_count:,} characters")
                self.file_info_label.setStyleSheet(f"color: {self.gui_config.colors.warning}; font-weight: bold;")
            elif not text:
                self.file_info_label.setText("Type or paste your text below, or load from a file")
                self.file_info_label.setStyleSheet(f"color: {self.gui_config.colors.text_secondary}; font-style: italic;")
        
        # Emit signal
        self.text_changed.emit(text)
    
    # Public API methods
    def set_title(self, title: str) -> None:
        """Set the section title."""
        self._title = title
        if self.section_label:
            self.section_label.setText(title)
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.text_input.toPlainText() if self.text_input else ""
    
    def set_text(self, text: str) -> None:
        """Set the text content."""
        if self.text_input:
            self.text_input.setPlainText(text)
    
    def get_file_path(self) -> Optional[str]:
        """Get the current file path."""
        return self.current_file_path
    
    def set_readonly(self, readonly: bool) -> None:
        """Set the text input as readonly."""
        if self.text_input:
            self.text_input.setReadOnly(readonly)
    
    def update_config(self, config: InputConfig) -> None:
        """Update input configuration and refresh UI."""
        self.config = config
        self.setup_ui()
        self.apply_styling()
    
    def set_theme(self, theme_name: str) -> None:
        """Apply a different theme to the input section."""
        self.gui_config.set_theme(theme_name)
        self.apply_styling()


# Backward compatibility - keep your original simple input
class InputSection(ConfigurableInputSection):
    """Simple input section for backward compatibility."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)