from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from PyQt6.QtGui import QFont # type: ignore


@dataclass
class ColorTheme:
    """Color theme configuration."""
    primary: str = "#2c3e50"
    secondary: str = "#3498db"
    accent: str = "#e74c3c"
    success: str = "#27ae60"
    warning: str = "#f39c12"
    danger: str = "#e74c3c"
    
    # Text colors
    text_primary: str = "#2c3e50"
    text_secondary: str = "#7f8c8d"
    text_muted: str = "#95a5a6"
    text_light: str = "#ecf0f1"
    
    # Background colors
    bg_primary: str = "#ffffff"
    bg_secondary: str = "#f8f9fa"
    bg_dark: str = "#34495e"
    
    # Border colors
    border_light: str = "#ecf0f1"
    border_medium: str = "#bdc3c7"
    border_dark: str = "#95a5a6"


@dataclass
class FontConfig:
    """Font configuration."""
    family_primary: str = "Segoe UI"
    family_monospace: str = "Consolas, Monaco, monospace"
    
    # Font sizes
    size_small: int = 9
    size_normal: int = 10
    size_medium: int = 11
    size_large: int = 14
    size_xlarge: int = 18
    size_title: int = 24
    
    # Font weights
    weight_normal: int = QFont.Weight.Normal.value
    weight_bold: int = QFont.Weight.Bold.value


@dataclass
class SpacingConfig:
    """Spacing and sizing configuration."""
    margin_small: int = 5
    margin_medium: int = 10
    margin_large: int = 20
    
    padding_small: int = 5
    padding_medium: int = 10
    padding_large: int = 15
    
    border_radius_small: int = 3
    border_radius_medium: int = 5
    border_radius_large: int = 8
    
    border_width_thin: int = 1
    border_width_medium: int = 2
    border_width_thick: int = 3


@dataclass
class HeaderConfig:
    """Header-specific configuration."""
    show_icon: bool = True
    icon_size: int = 32
    title_alignment: str = "center"  # left, center, right
    subtitle_alignment: str = "center"
    background_gradient: bool = False
    shadow_enabled: bool = True
    
    # Custom styling
    custom_title_style: Optional[str] = None
    custom_subtitle_style: Optional[str] = None
    custom_background_style: Optional[str] = None

@dataclass
class InputConfig:
    """Input section specific configuration."""
    show_file_controls: bool = True
    show_character_count: bool = True
    show_file_info: bool = True
    min_height: int = 200
    max_height: int = 400
    placeholder_text: str = "Enter your text here..."
    
    # File dialog settings
    supported_extensions: str = "Text Files (*.txt *.md *.py *.js *.html *.css *.json *.xml);;All Files (*)"
    default_directory: str = ""
    
    # Button configurations
    load_button_text: str = "📁 Load File"
    clear_button_text: str = "🗑️ Clear"
    show_load_button: bool = True
    show_clear_button: bool = True
    
    # Text area settings
    word_wrap: bool = True
    font_family: str = "Consolas, Monaco, monospace"
    font_size: int = 10
    line_height: float = 1.4
    
    # Custom styling
    custom_frame_style: Optional[str] = None
    custom_textarea_style: Optional[str] = None
    custom_button_style: Optional[str] = None

@dataclass
class SearchConfig:
    """Search section specific configuration."""
    # Keywords section
    show_keywords_section: bool = True
    keywords_placeholder: str = "Enter keywords separated by commas (e.g., python, algorithm, search)"
    max_keywords_display_height: int = 80
    
    # Algorithm section
    show_algorithm_section: bool = True
    default_algorithm: str = "KMP (Knuth-Morris-Pratt)"
    available_algorithms: tuple = (
        "KMP (Knuth-Morris-Pratt)",
        "Boyer-Moore Simple",
        "Boyer-Moore Complex",
        "Aho-Corasick",
        "Fuzzy Search"
    )
    
    # Search parameters
    default_top_matches: int = 10
    max_top_matches: int = 1000
    default_case_sensitive: bool = False
    
    # Button configurations
    search_button_text: str = "🔍 Start Search"
    searching_button_text: str = "🔄 Searching..."
    add_keyword_text: str = "+ Add"
    clear_keywords_text: str = "Clear All"
    
    # Display settings
    show_algorithm_info: bool = True
    show_quick_add_buttons: bool = True
    show_search_parameters: bool = True
    
    # Custom styling
    custom_frame_style: Optional[str] = None
    custom_button_style: Optional[str] = None
    custom_input_style: Optional[str] = None

@dataclass
class ResultConfig:
    """Result section specific configuration."""
    # Display settings
    show_statistics: bool = True
    show_export_button: bool = True
    show_clear_button: bool = True
    show_progress_bar: bool = True
    
    # Card settings
    max_snippet_length: int = 200
    snippet_height: int = 80
    card_hover_effect: bool = True
    show_pattern_highlighting: bool = True
    show_similarity_score: bool = True
    
    # Export settings
    default_export_format: str = "txt"  # txt, csv, json
    supported_export_formats: str = "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json)"
    
    # Button configurations
    export_button_text: str = "💾 Export Results"
    clear_button_text: str = "🗑️ Clear Results"
    
    # Display texts
    title_text: str = "📊 Search Results"
    empty_state_message: str = "🔍 No search results yet\n\nEnter your text and keywords above, then click 'Start Search' to find patterns."
    no_results_message: str = "❌ No matches found\n\nTry different keywords or switch to fuzzy search for approximate matches."
    
    # Animation and interaction
    enable_animations: bool = True
    enable_card_selection: bool = True
    auto_scroll_to_results: bool = True
    
    # Custom styling
    custom_header_style: Optional[str] = None
    custom_card_style: Optional[str] = None
    custom_empty_state_style: Optional[str] = None

class GUIConfig:
    """Central GUI configuration manager."""
    
    def __init__(self):
        self.colors = ColorTheme()
        self.fonts = FontConfig()
        self.spacing = SpacingConfig()
        self.header = HeaderConfig()
        self.search = SearchConfig()
        self.result = ResultConfig()
        self._custom_themes: Dict[str, ColorTheme] = {}
    
    def set_theme(self, theme_name: str) -> None:
        """Set a predefined theme."""
        themes = {
            "light": ColorTheme(),
            "dark": ColorTheme(
                primary="#ecf0f1",
                text_primary="#ecf0f1",
                text_secondary="#bdc3c7",
                bg_primary="#2c3e50",
                bg_secondary="#34495e",
                border_light="#34495e",
                border_medium="#7f8c8d"
            ),
            "blue": ColorTheme(
                primary="#3498db",
                secondary="#2980b9",
                bg_secondary="#ebf3fd"
            )
        }
        
        if theme_name in themes:
            self.colors = themes[theme_name]
        elif theme_name in self._custom_themes:
            self.colors = self._custom_themes[theme_name]
    
    def register_custom_theme(self, name: str, theme: ColorTheme) -> None:
        """Register a custom color theme."""
        self._custom_themes[name] = theme
    
    def get_style_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary for easy template substitution."""
        return {
            'colors': self.colors.__dict__,
            'fonts': self.fonts.__dict__,
            'spacing': self.spacing.__dict__,
            'header': self.header.__dict__
        }


# Global configuration instance
gui_config = GUIConfig()