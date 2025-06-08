"""
Examples of how to use the configurable header component.
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget # type: ignore
from src.gui_components.header import ConfigurableHeaderComponent
from src.gui_components.general_config import gui_config, HeaderConfig, ColorTheme
import sys


def create_basic_header():
    """Create a basic header with default settings."""
    return ConfigurableHeaderComponent(
        title="My Application",
        subtitle="A simple and elegant tool"
    )


def create_custom_styled_header():
    """Create a header with custom styling."""
    config = HeaderConfig(
        show_icon=True,
        icon_size=48,
        title_alignment="left",
        background_gradient=True,
        shadow_enabled=True,
        custom_title_style="font-weight: 900; letter-spacing: 2px;",
        custom_subtitle_style="font-style: italic; opacity: 0.8;"
    )
    
    return ConfigurableHeaderComponent(
        title="Advanced Tool",
        subtitle="Sophisticated pattern matching and analysis",
        config=config
    )


def create_dark_theme_header():
    """Create a header with dark theme."""
    # Set dark theme globally
    gui_config.set_theme("dark")
    
    return ConfigurableHeaderComponent(
        title="Dark Mode App",
        subtitle="Sleek and modern interface"
    )


def create_minimal_header():
    """Create a minimal header without subtitle."""
    config = HeaderConfig(
        show_icon=False,
        title_alignment="center",
        shadow_enabled=False
    )
    
    return ConfigurableHeaderComponent(
        title="Minimal Design",
        subtitle="",  # No subtitle
        config=config
    )


# Example usage in a main window
class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Header Component Examples")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add different header examples
        layout.addWidget(create_basic_header())
        layout.addWidget(create_custom_styled_header())
        layout.addWidget(create_minimal_header())
        
        layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())