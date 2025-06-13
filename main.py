import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from src.gui_components.header import HeaderComponent
from src.gui_components.search import SearchControls
from src.gui_components.result import ResultsSection
from src.service.searchservice import SearchService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applicant Tracking System")
        self.setGeometry(100, 100, 900, 700)

        # --- UI Setup ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.header = HeaderComponent()
        self.search_section = SearchControls()
        self.result_section = ResultsSection()
        self.status_label = QLabel("Ready. Enter a keyword to begin.")

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.search_section)
        main_layout.addWidget(self.result_section)
        main_layout.addWidget(self.status_label)
        main_layout.setStretch(2, 1)

        # --- Initialize the Search Service ---
        self.search_service = SearchService(self)

        # --- Connect the search button's click signal to the on_search method ---
        self.search_section.search_btn.clicked.connect(self.on_search)

    def on_search(self):
        """
        This method is called when the user clicks the search button.
        It gets the user's input and tells the SearchService to start.
        """
        keyword = self.search_section.keywords_input.text()
        search_type = self.search_section.algorithm_combo.currentText()
        top_k = self.search_section.top_k_spinbox.value()

        if not keyword:
            self.update_status("Please enter a keyword.")
            return

        self.search_service.start_search(keyword, search_type, top_k)

    def display_search_results(self, results, execution_time):
        """
        This is a "slot" that is called when the SearchWorker emits its
        'finished' signal. It receives the results and updates the UI.
        """
        self.result_section.display_results(results)
        self.search_section.search_button.setEnabled(True)
        self.update_status(f"Search complete in {execution_time:.2f} seconds. Found {len(results)} results.")

    def update_status(self, message):
        """
        This "slot" is called by the SearchWorker's 'progress' signal
        to update the status label in the UI.
        """
        self.status_label.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())

