import os
import time
import concurrent.futures
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from collections import Counter
from ..database.models import SessionLocal, ApplicationDetail
from ..database.pdf_utils import extract_text_from_pdf, prepare_texts_from_pdf, save_extracted_texts
from ..search_algorithms.search_engine import SearchEngine, AlgorithmType, SearchMatch
from ..config.config import CV_FOLDER

@dataclass
class CVMatch:
    applicant_id: int
    resume_id: str
    score: int
    cv_path: str
    occurrences: Dict[str, int]

# ini gajadi dipake tapi gpp dh keep aja dl
@dataclass
class ApplicantResult:
    applicant_id: int
    resumes: List[CVMatch]

class SearchService:
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers
        self.engine = SearchEngine()
        # Just keep one cache for now - the pattern cache for searches
        self.text_cache_pattern = {}
        # Keep regex cache structure but don't populate it yet
        self.text_cache_regex = {}
        
    def preprocess_cvs(self, progress_callback=None):
        """Use pdf_utils functions directly to avoid redundant processing"""
        try:
            db = SessionLocal()
            resumes = db.query(ApplicationDetail).all()
        finally:
            db.close()

        start = time.time()
        total = len(resumes)
        processed = 0
        
        # Create cache directory
        cache_dir = os.path.join(os.path.dirname(CV_FOLDER), "cache")
        os.makedirs(cache_dir, exist_ok=True)

        def process_cv(resume):
            pdf_path = os.path.join(CV_FOLDER, resume.cv_file_name + ".pdf")
            if not os.path.exists(pdf_path):
                return None
            
            # Define cache files for pattern format
            cache_pattern = os.path.join(cache_dir, f"{resume.cv_file_name}_pattern.txt")
            
            # Check if we need to parse the PDF
            need_parsing = True
            if os.path.exists(cache_pattern):
                pdf_mtime = os.path.getmtime(pdf_path)
                cache_mtime = os.path.getmtime(cache_pattern)
                
                # Use cache if it's newer than the PDF
                if cache_mtime > pdf_mtime:
                    need_parsing = False
                    # Read pattern text from cache
                    with open(cache_pattern, 'r', encoding='utf-8') as f:
                        text_pattern = f.read()
                    return resume.cv_file_name, text_pattern
            
            # Parse PDF if needed
            if need_parsing:
                # Use prepare_texts_from_pdf which handles both extraction and formatting
                result = prepare_texts_from_pdf(pdf_path)
                if result is None:
                    return None
                    
                # Get the processed text for pattern searching (second item in tuple)
                text_regex, text_pattern = result
                
                # Use save_extracted_texts to save both formats
                # We're only using pattern format now, but we'll save regex too for future use
                regex_cache = os.path.join(cache_dir, f"{resume.cv_file_name}_regex.txt")
                save_extracted_texts(pdf_path, regex_cache, cache_pattern)
                
                return resume.cv_file_name, text_pattern
                
            return None

        # Process CVs in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for result in executor.map(process_cv, resumes):
                if result:
                    cv_id, text_pattern = result
                    self.text_cache_pattern[cv_id] = text_pattern
                    
                processed += 1
                if progress_callback:
                    progress_callback(processed)

        elapsed = time.time() - start
        return elapsed, len(self.text_cache_pattern)

    def search(self, keywords: str, algorithm: str, top_k: int, case: bool, progress_callback=None) -> Tuple[int, float, List[CVMatch]]:
        """
        :param keywords: pattern(s) to search, space-separated
        :param algorithm: 'fuzzy' or one of exact algorithm names
        :param top_k: number of top CVs to return
        :return: total_scanned, search_time, list of CVMatch
        """
        # Split keywords by spaces
        keyword_list = [kw.strip() if case else kw.strip().lower() for kw in keywords.replace(',', ' ').split() if kw.strip()]
        if not keyword_list:
            return 0, 0.0, []
            
        # Load resumes
        db = SessionLocal()
        resumes = db.query(ApplicationDetail).all()
        db.close()

        total_scanned = len(self.text_cache_pattern)
        start_time = time.time()
        all_matches: List[CVMatch] = []
        
        # Initialize the processed variable before using it
        processed = 0  # Add this line
    
        def process(resume) -> Optional[CVMatch]:
            pdf_path = os.path.join(CV_FOLDER, resume.cv_file_name + ".pdf")
            if not os.path.exists(pdf_path):
                return None
                
            # Use text_cache_pattern if available
            if resume.cv_file_name in self.text_cache_pattern:
                text = self.text_cache_pattern[resume.cv_file_name]
            else:
                # If not cached in memory, use prepare_texts_from_pdf
                result = prepare_texts_from_pdf(pdf_path)
                if result is None:
                    return None
                    
                # Get the pattern text (second item)
                _, text = result
                self.text_cache_pattern[resume.cv_file_name] = text
                
            all_matches = []
            
            # Search for each keyword separately
            for keyword in keyword_list:
                # Choose search mode
                if algorithm.lower() == 'fuzzy':
                    matches, _ = self.engine.search_fuzzy_only(text, keyword)
                else:
                    try:
                        algo = AlgorithmType(algorithm.lower())
                    except ValueError:
                        algo = self.engine.config.exact_algorithm
                    matches, _ = self.engine.search_exact_only(text, keyword, algo)
                    
                all_matches.extend(matches)
                
            if not all_matches:
                return None
                
            # Count occurrences of each matched pattern
            counts = Counter(match.pattern for match in all_matches)
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
                    all_matches.append(match)
                
                # Move this outside the if condition so it counts all processed items
                processed += 1
                if progress_callback and total_scanned > 0:
                    # Calculate percentage progress (0-100)
                    progress = min(100, int((processed / len(resumes)) * 100))
                    progress_callback(progress)

        # Sort CVs directly by score
        all_matches.sort(key=lambda m: m.score, reverse=True)
        elapsed = time.time() - start_time

        return total_scanned, elapsed, all_matches[:top_k]