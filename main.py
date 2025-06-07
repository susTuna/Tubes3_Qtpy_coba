import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,  # type: ignore
                           QHBoxLayout, QScrollArea, QSplitter, QFrame)
from PyQt6.QtCore import Qt, QSize # type: ignore
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon # type: ignore

from src.gui_components.header import HeaderComponent
from src.gui_components.input import InputSection
from src.gui_components.search import SearchControls
from src.gui_components.result import ResultsSection

from typing import Optional


class StringMatchingApp(QMainWindow):
    """Main application window for the String Matching Toolkit."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.setup_styling()
        self.connect_signals()
    
    def setup_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle("String Matching Toolkit - Advanced Pattern Search")
        self.setMinimumSize(QSize(1200, 800))
        self.resize(QSize(1400, 900))
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except:
            pass  # Icon file not found, continue without it
        
        # Center the window on screen
        self.center_window()
    
    def center_window(self) -> None:
        """Center the window on the screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def setup_ui(self) -> None:
        """Set up the main user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self.header = HeaderComponent()
        main_layout.addWidget(self.header)
        
        # Create splitter for resizable sections
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        
        # Left panel (Input and Search Controls)
        self.left_panel = self.create_left_panel()
        
        # Right panel (Results)
        self.right_panel = self.create_right_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set splitter proportions (40% left, 60% right)
        self.main_splitter.setSizes([560, 840])
        self.main_splitter.setStretchFactor(0, 0)  # Left panel fixed-ish
        self.main_splitter.setStretchFactor(1, 1)  # Right panel stretches
        
        main_layout.addWidget(self.main_splitter)
        
        # Status bar for additional info
        self.setup_status_bar()
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with input and search controls."""
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.NoFrame)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 2px solid #e9ecef;
            }
        """)
        
        # Create scrollable area for left panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 20)
        content_layout.setSpacing(20)
        
        # Add input section
        self.input_section = InputSection()
        content_layout.addWidget(self.input_section)
        
        # Add search controls
        self.search_controls = SearchControls()
        content_layout.addWidget(self.search_controls)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # Layout for left panel
        panel_layout = QVBoxLayout(left_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)
        
        return left_panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with results."""
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.NoFrame)
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
            }
        """)
        
        panel_layout = QVBoxLayout(right_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add results section
        self.results_section = ResultsSection()
        panel_layout.addWidget(self.results_section)
        
        return right_panel
    
    def setup_status_bar(self) -> None:
        """Set up the status bar."""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: #ecf0f1;
                border-top: 1px solid #2c3e50;
                padding: 5px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Set initial status
        status_bar.showMessage("Ready to search - Load text and enter keywords to begin", 0)
    
    def setup_styling(self) -> None:
        """Set up application-wide styling."""
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
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
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: #ecf0f1;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #95a5a6;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QSplitter::handle {
                background-color: #bdc3c7;
                border: 1px solid #95a5a6;
            }
            
            QSplitter::handle:horizontal {
                width: 3px;
            }
            
            QSplitter::handle:vertical {
                height: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
    
    def connect_signals(self) -> None:
        """Connect signals between components."""
        # Connect input section signals
        self.input_section.text_changed.connect(self.on_text_changed)
        self.input_section.file_loaded.connect(self.on_file_loaded)
        
        # Connect search controls signals
        self.search_controls.search_requested.connect(self.on_search_requested)
        
        # Connect results section signals
        self.results_section.result_selected.connect(self.on_result_selected)
    
    # Signal handlers (to be implemented by controller)
    def on_text_changed(self, text: str) -> None:
        """Handle text change events."""
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        
        if char_count == 0:
            self.statusBar().showMessage("Ready to search - Load text and enter keywords to begin")
        else:
            self.statusBar().showMessage(f"Text loaded: {char_count:,} characters, {word_count:,} words")
    
    def on_file_loaded(self, filename: str, content: str) -> None:
        """Handle file load events."""
        char_count = len(content)
        word_count = len(content.split()) if content.strip() else 0
        self.statusBar().showMessage(f"File loaded: {filename} - {char_count:,} characters, {word_count:,} words")
    
    def on_search_requested(self, search_params: dict) -> None:
        """Handle search request events."""
        # Show search in progress
        self.results_section.show_search_progress("Searching...")
        self.statusBar().showMessage("Search in progress...")
        
        # This will be handled by the controller
        print("Search requested with parameters:", search_params)
    
    def on_result_selected(self, result_data: dict) -> None:
        """Handle result selection events."""
        # This will be handled by the controller
        print("Result selected:", result_data)
    
    # Public methods for controller interface
    def get_text_content(self) -> str:
        """Get the current text content."""
        return self.input_section.get_text()
    
    def get_search_parameters(self) -> dict:
        """Get current search parameters."""
        return self.search_controls.get_search_params()
    
    def display_search_results(self, results: list, search_time: float, search_params: dict) -> None:
        """Display search results."""
        self.results_section.display_results(results, search_time, search_params)
        
        result_count = len(results)
        if result_count == 0:
            self.statusBar().showMessage("Search completed - No matches found")
        else:
            self.statusBar().showMessage(f"Search completed - {result_count} matches found in {search_time:.3f}s")
    
    def show_error_message(self, message: str) -> None:
        """Show error message."""
        self.statusBar().showMessage(f"Error: {message}", 5000)  # Show for 5 seconds
    
    def set_search_enabled(self, enabled: bool) -> None:
        """Enable or disable search functionality."""
        self.search_controls.set_search_enabled(enabled)


class ResponsiveStringMatchingApp(StringMatchingApp):
    """Responsive version of the String Matching App with adaptive layout."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setup_responsive_features()
    
    def setup_responsive_features(self) -> None:
        """Set up responsive UI features."""
        # Monitor window resize events
        self.resizeEvent = self.on_window_resize
    
    def on_window_resize(self, event) -> None:
        """Handle window resize events for responsive design."""
        super().resizeEvent(event)
        
        # Adjust layout based on window size
        window_width = self.width()
        
        if window_width < 1000:
            # Small window - stack vertically
            self.main_splitter.setOrientation(Qt.Orientation.Vertical)
            self.main_splitter.setSizes([400, 400])
        else:
            # Large window - side by side
            self.main_splitter.setOrientation(Qt.Orientation.Horizontal)
            self.main_splitter.setSizes([int(window_width * 0.4), int(window_width * 0.6)])


def create_application() -> QApplication:
    """Create and configure the QApplication."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("String Matching Toolkit")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Advanced Algorithms Lab")
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Set application palette for better theming
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#ecf0f1"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#34495e"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ecf0f1"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e9ecef"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2c3e50"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#e74c3c"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#3498db"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    app.setPalette(palette)
    
    return app


def main() -> None:
    """Main application entry point."""
    # Create application
    app = create_application()
    
    # Create main window
    window = ResponsiveStringMatchingApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()