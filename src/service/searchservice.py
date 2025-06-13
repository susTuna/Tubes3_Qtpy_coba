import os
import time
import concurrent.futures
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from collections import Counter
from ..database.models import SessionLocal, ApplicationDetail
from ..database.pdf_utils import extract_text_from_pdf
from ..database.parser import parse_text
from ..search_algorithms.search_engine import SearchEngine, AlgorithmType, SearchMatch
from ..config.config import CV_FOLDER

@dataclass
class CVMatch:
    applicant_id: int
    resume_id: str
    score: int
    cv_path: str
    occurrences: Dict[str, int]

@dataclass
class ApplicantResult:
    applicant_id: int
    resumes: List[CVMatch]

class SearchService:
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers
        self.engine = SearchEngine()

    def search(self, keywords: str, algorithm: str, top_k: int) -> Tuple[int, float, List[ApplicantResult]]:
        """
        :param keywords: pattern(s) to search
        :param algorithm: 'fuzzy' or one of exact algorithm names
        :param top_k: number of top applicants to return
        :return: total_scanned, search_time, list of ApplicantResult
        """
        # Load resumes
        db = SessionLocal()
        resumes = db.query(ApplicationDetail).all()
        db.close()

        total_scanned = len(resumes)
        start_time = time.time()
        temp: Dict[int, List[CVMatch]] = {}

        def process(resume) -> Optional[CVMatch]:
            pdf_path = os.path.join(CV_FOLDER, resume.cv_file_name + ".pdf")
            if not os.path.exists(pdf_path):
                return None
            text = parse_text(extract_text_from_pdf(pdf_path))
            # choose search mode
            if algorithm.lower() == 'fuzzy':
                matches, _ = self.engine.search_fuzzy_only(text, keywords)
            else:
                try:
                    algo = AlgorithmType(algorithm.lower())
                except ValueError:
                    algo = self.engine.config.exact_algorithm
                matches, _ = self.engine.search_exact_only(text, keywords, algo)
            if not matches:
                return None
            # count occurrences of each matched pattern
            counts = Counter(match.pattern for match in matches)
            score = sum(counts.values())
            return CVMatch(
                applicant_id=resume.applicant_id,
                resume_id=resume.cv_file_name,
                score=score,
                cv_path=pdf_path,
                occurrences=dict(counts)
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for match in executor.map(process, resumes):
                if match:
                    temp.setdefault(match.applicant_id, []).append(match)

        results: List[ApplicantResult] = []
        for aid, cv_list in temp.items():
            results.append(ApplicantResult(applicant_id=aid, resumes=cv_list))
        results.sort(key=lambda a: sum(cv.score for cv in a.resumes), reverse=True)
        elapsed = time.time() - start_time

        return total_scanned, elapsed, results[:top_k]