from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any, Optional

class PreprocessThread(QThread):
    """Thread for preprocessing CVs in background"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, float)  # count, elapsed_time
    
    def __init__(self, service):
        super().__init__()
        self.service = service
        
    def run(self):
        elapsed, count = self.service.preprocess_cvs(progress_callback=self.progress.emit)
        self.finished.emit(count, elapsed)

class SearchThread(QThread):
    """Thread for searching CVs in background"""
    progress = pyqtSignal(int)
    results_ready = pyqtSignal(int, float, list)  # total_docs, elapsed_time, results
    
    def __init__(self, service, keywords, algorithm, top_k, case_sensitive):
        super().__init__()
        self.service = service
        self.keywords = keywords
        self.algorithm = algorithm
        self.top_k = top_k
        self.case_sensitive = case_sensitive
        
    def run(self):
        total, elapsed, results = self.service.search(
            self.keywords, 
            self.algorithm,
            self.top_k,
            self.case_sensitive,
            progress_callback=self.progress.emit
        )
        self.results_ready.emit(total, elapsed, results)