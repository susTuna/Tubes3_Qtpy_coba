import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.service.searchservice import SearchService
from src.database.models import SessionLocal, ApplicantProfile
from PyQt6.QtWidgets import QApplication
from src.gui_components.cv_summary_window import CVSummaryWindow

def main():
    print("=== CV Finder ===")
    keywords = input("Enter keywords to search for: ").strip()

    service = SearchService(max_workers=4)
    algo_list = service.engine.get_available_algorithms() + ['fuzzy']
    print(f"Available algorithms: {', '.join(algo_list)}")
    algorithm = input("Choose algorithm: ").strip().lower()
    if algorithm not in [a.lower() for a in algo_list]:
        print(f"Unknown algorithm '{algorithm}', defaulting to fuzzy.")
        algorithm = 'fuzzy'

    try:
        top_k = int(input("Enter number of top matches to display: ").strip())
    except ValueError:
        print("Invalid number, defaulting to 5.")
        top_k = 5

    total, elapsed, matches = service.search(keywords, algorithm, top_k)
    print(f"\nScanned {total} CVs in {elapsed:.2f} seconds.\n")

    if not matches:
        print("No matches found.")
        return

    session = SessionLocal()
    
    # Disini bisa print CLI kalau mau, well ini
    for idx, result in enumerate(matches, start=1):
        profile = session.query(ApplicantProfile).get(result.applicant_id)
        name = f"{profile.first_name} {profile.last_name}" if profile else f"Applicant {result.applicant_id}"
        total_score = sum(cv.score for cv in result.resumes)
        print(f"{idx}. {name} (ID: {result.applicant_id}) — Total Score: {total_score}")
        for cv in result.resumes:
            print(f"    • {cv.resume_id} | Score: {cv.score} | Path: {cv.cv_path}")
    #=====================================================


    # Now launch GUI for the *first* applicant:
    top = matches[0]
    profile = session.query(ApplicantProfile).get(top.applicant_id)
    name      = f"{profile.first_name} {profile.last_name}"
    birthdate = profile.birthdate.strftime("%m-%d-%Y") if profile.birthdate else ""
    address   = profile.address or ""
    phone     = profile.phone   or ""
    skills    = [s.strip() for s in keywords.split(",")]
    jobs      = [{"title": m.resume_id, "period": "N/A", "description": f"Score: {m.score}"} for m in top.resumes]
    education = [{"degree":"N/A","institution":"","period":""}]

    app = QApplication(sys.argv)
    win = CVSummaryWindow(name, birthdate, address, phone, skills, jobs, education)
    win.show()
    app.exec()

    session.close()

if __name__ == '__main__':
    main()
