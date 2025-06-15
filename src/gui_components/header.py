from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame # type: ignore
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont, QPixmap, QIcon # type: ignore
from typing import Optional, Union, Literal
from .general_config import gui_config, HeaderConfig


class ConfigurableHeaderComponent(QWidget):
    """Highly configurable header component for the application."""
    
    # Signals
    title_clicked = pyqtSignal()
    subtitle_clicked = pyqtSignal()
    
    def __init__(self, 
                 title: str = "CV PROCESSOR",
                 subtitle: str = "Advanced pattern matching with KMP, Boyer-Moore, Aho-Corasick, and Fuzzy Search",
                 icon_path: Optional[str] = None,
                 config: Optional[HeaderConfig] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Configuration
        self.config = config or gui_config.header
        self.gui_config = gui_config
        
        # Content
        self._title = title
        self._subtitle = subtitle
        self._icon_path = icon_path
        
        # UI Elements
        self.container_frame: Optional[QFrame] = None
        self.icon_label: Optional[QLabel] = None
        self.title_label: Optional[QLabel] = None
        self.subtitle_label: Optional[QLabel] = None
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the header UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container frame for styling
        self.container_frame = QFrame()
        self.container_frame.setObjectName("headerContainer")
        
        # Main content layout
        content_layout = QVBoxLayout(self.container_frame)
        content_layout.setContentsMargins(
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_large,
            self.gui_config.spacing.margin_medium
        )
        content_layout.setSpacing(self.gui_config.spacing.margin_small)
        
        # Header content layout (for icon + text)
        header_content_layout = QHBoxLayout()
        
        # Icon (if enabled and provided)
        if self.config.show_icon and self._icon_path:
            self.setup_icon(header_content_layout)
        
        # Text content layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(self.gui_config.spacing.margin_small)
        
        # Title
        self.setup_title(text_layout)
        
        # Subtitle
        if self._subtitle:
            self.setup_subtitle(text_layout)
        
        # Add text layout to header content
        header_content_layout.addLayout(text_layout)
        
        # Add header content to main content
        content_layout.addLayout(header_content_layout)
        
        # Add container to main layout
        main_layout.addWidget(self.container_frame)
        
        # Apply styling
        self.apply_styling()
    
    def setup_icon(self, layout: QHBoxLayout) -> None:
        """Set up the header icon."""
        self.icon_label = QLabel()
        self.icon_label.setObjectName("headerIcon")
        
        # Load and set icon
        pixmap = QPixmap(self._icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.config.icon_size, 
                self.config.icon_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.icon_label.setPixmap(scaled_pixmap)
        
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
    
    def setup_title(self, layout: QVBoxLayout) -> None:
        """Set up the title label."""
        self.title_label = QLabel(self._title)
        self.title_label.setObjectName("headerTitle")
        
        # Alignment
        alignment_map = {
            "left": Qt.AlignmentFlag.AlignLeft,
            "center": Qt.AlignmentFlag.AlignCenter,
            "right": Qt.AlignmentFlag.AlignRight
        }
        self.title_label.setAlignment(alignment_map.get(self.config.title_alignment, Qt.AlignmentFlag.AlignCenter))
        
        # Font
        title_font = QFont(self.gui_config.fonts.family_primary)
        title_font.setPointSize(self.gui_config.fonts.size_title)
        title_font.setWeight(QFont.Weight(self.gui_config.fonts.weight_bold))
        self.title_label.setFont(title_font)
        
        # Make clickable if needed
        self.title_label.mousePressEvent = lambda e: self.title_clicked.emit()
        
        layout.addWidget(self.title_label)
    
    def setup_subtitle(self, layout: QVBoxLayout) -> None:
        """Set up the subtitle label."""
        self.subtitle_label = QLabel(self._subtitle)
        self.subtitle_label.setObjectName("headerSubtitle")
        
        # Alignment
        alignment_map = {
            "left": Qt.AlignmentFlag.AlignLeft,
            "center": Qt.AlignmentFlag.AlignCenter,
            "right": Qt.AlignmentFlag.AlignRight
        }
        self.subtitle_label.setAlignment(alignment_map.get(self.config.subtitle_alignment, Qt.AlignmentFlag.AlignCenter))
        
        # Font
        subtitle_font = QFont(self.gui_config.fonts.family_primary)
        subtitle_font.setPointSize(self.gui_config.fonts.size_medium)
        subtitle_font.setWeight(QFont.Weight(self.gui_config.fonts.weight_normal))
        self.subtitle_label.setFont(subtitle_font)
        
        # Word wrap for long subtitles
        self.subtitle_label.setWordWrap(True)
        
        # Make clickable if needed
        self.subtitle_label.mousePressEvent = lambda e: self.subtitle_clicked.emit()
        
        layout.addWidget(self.subtitle_label)
    
    def apply_styling(self) -> None:
        """Apply CSS styling to the header components."""
        # Base container style
        container_style = f"""
        QFrame#headerContainer {{
            background-color: {self.gui_config.colors.bg_primary};
            border: none;
            {self._get_background_style()}
        }}
        """
        
        # Title style
        title_style = f"""
        QLabel#headerTitle {{
            color: {self.gui_config.colors.text_primary};
            margin: {self.gui_config.spacing.margin_medium}px 0;
            {self._get_title_effects()}
        }}
        QLabel#headerTitle:hover {{
            color: {self.gui_config.colors.secondary};
        }}
        """
        
        # Subtitle style
        subtitle_style = f"""
        QLabel#headerSubtitle {{
            color: {self.gui_config.colors.text_secondary};
            margin-bottom: {self.gui_config.spacing.margin_large}px;
            line-height: 1.4;
        }}
        QLabel#headerSubtitle:hover {{
            color: {self.gui_config.colors.text_primary};
        }}
        """
        
        # Combine and apply styles
        full_style = container_style + title_style + subtitle_style
        
        # Apply custom styles if provided
        if self.config.custom_title_style and self.title_label:
            full_style += f"QLabel#headerTitle {{ {self.config.custom_title_style} }}"
        
        if self.config.custom_subtitle_style and self.subtitle_label:
            full_style += f"QLabel#headerSubtitle {{ {self.config.custom_subtitle_style} }}"
        
        if self.config.custom_background_style:
            full_style += f"QFrame#headerContainer {{ {self.config.custom_background_style} }}"
        
        self.setStyleSheet(full_style)
    
    def _get_background_style(self) -> str:
        """Get background styling based on configuration."""
        if self.config.background_gradient:
            return f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.gui_config.colors.bg_primary},
                stop:1 {self.gui_config.colors.bg_secondary});
            """
        return ""
    
    def _get_title_effects(self) -> str:
        """Get title effects based on configuration."""
        effects = ""
        if self.config.shadow_enabled:
            effects += "text-shadow: 1px 1px 2px rgba(0,0,0,0.1);"
        return effects
    
    # Public API methods
    def set_title(self, title: str) -> None:
        """Set the header title."""
        self._title = title
        if self.title_label:
            self.title_label.setText(title)
    
    def set_subtitle(self, subtitle: str) -> None:
        """Set the header subtitle."""
        self._subtitle = subtitle
        if self.subtitle_label:
            self.subtitle_label.setText(subtitle)
        elif subtitle:  # Create subtitle if it doesn't exist
            self.setup_ui()  # Rebuild UI
    
    def set_icon(self, icon_path: str) -> None:
        """Set the header icon."""
        self._icon_path = icon_path
        if self.icon_label:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.config.icon_size, 
                    self.config.icon_size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.icon_label.setPixmap(scaled_pixmap)
    
    def update_config(self, config: HeaderConfig) -> None:
        """Update header configuration and refresh UI."""
        self.config = config
        self.setup_ui()
    
    def set_theme(self, theme_name: str) -> None:
        """Apply a different theme to the header."""
        self.gui_config.set_theme(theme_name)
        self.apply_styling()


# Backward compatibility - keep your original simple header
class HeaderComponent(ConfigurableHeaderComponent):
    """Simple header component for backward compatibility."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)