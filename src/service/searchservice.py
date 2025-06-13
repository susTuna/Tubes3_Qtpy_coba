from PyQt6.QtCore import QObject, pyqtSignal, QThread
from ..database.models import SessionLocal, ApplicationDetail, ApplicantProfile
from ..database.pdf_utils import extract_text_from_pdf
from ..database.parser import parse_for_regex, parse_text
from ..search_algorithms.search_engine import SearchEngine
from ..config.config import CV_FOLDER
import os
import time
import concurrent.futures

class SearchWorker(QObject):

    finished = pyqtSignal(object, float)

    progress = pyqtSignal(str)

    def __init__(self, keyword, search_type, top_k):
        super().__init__()
        self.keyword = keyword
        self.search_type = search_type
        self.top_k = top_k
        self.search_engine = SearchEngine()
        self.processed_count = 0
        self.total_resumes = 0

    def process_single_resume(self, resume):
        file_path = os.path.join(CV_FOLDER, resume.cv_file_name + ".pdf")
        if os.path.exists(file_path):
            text = parse_text(extract_text_from_pdf(file_path))

            if self.search_type.lower() == "fuzzy":
                match_score = self.search_engine.fuzzy_search(text, self.keyword)
            else:
                match_found = self.search_engine.exact_search(text, self.keyword)
                match_score = 1 if match_found else 0
            
            self.processed_count += 1
            self.progress.emit(f"Processed {self.processed_count} / {self.total_resumes} resumes...")

            if match_score > 0:
                return { resume.applicant_id : 
                    { 
                        "resume_id": resume.cv_file_name,
                        "score": match_score,
                        "file_path": file_path
                    }
                }
        
        return None

    def run(self):
        start_time = time.time()
        db = SessionLocal()
        resumes = db.query(ApplicationDetail).all()
        applicants = db.query(ApplicantProfile).all()
        db.close()
        results = { applicant.applicant_id: {"resumes": []} for applicant in applicants }

        self.total_resumes = len(resumes)
        self.processed_count = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_results = executor.map(self.process_single_resume, resumes)
            for result in future_results:
                if result:
                    for applicant_id, resume_data in future_results.items():
                        if applicant_id in results:
                            results[applicant_id]["resumes"].append(resume_data)

        sorted_results = sorted(
            results.items(),
            key=lambda item: sum(resume["score"] for resume in item[1]["resumes"]),
            reverse=True
        )
        end_time = time.time()
        execution_time = end_time - start_time
        self.finished.emit(sorted_results[:self.top_k], execution_time)

class SearchService():
    def __init__(self, parent):
        self.parent = parent
        self.thread = None
        self.worker = None

    def start_search(self, keyword, search_type, top_k):
        self.thread = QThread()
        self.worker = SearchWorker(keyword, search_type, top_k)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.parent.display_search_results)
        self.worker.progress.connect(self.parent.update_status)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        self.parent.search_section.search_button.setEnabled(False)
        self.parent.status_label.setText("Searching resumes... Please wait.")

    
