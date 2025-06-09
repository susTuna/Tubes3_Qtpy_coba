import os
from src.database.models import SessionLocal, ApplicationDetail, ApplicantProfile, init_db
from src.database.pdf_utils import extract_text_from_pdf
from src.database.parser import parse_sections

from config.config import CV_FOLDER

def process_folder_and_update():
    init_db()
    db = SessionLocal()

    for filename in os.listdir(CV_FOLDER):
        if not filename.lower().endswith(".pdf"):
            continue
        file_path = os.path.join(CV_FOLDER, filename)
        full_text = extract_text_from_pdf(file_path)

        # basic identity seeding:
        applicant_id = os.path.splitext(filename)[0]
        # you could try to pull `name`, `phone` via regex, e.g.
        name_match = re.search(r"Name[:\-]\s*(.+)", full_text)
        name = name_match.group(1).split("\n")[0].strip() if name_match else None

        # parse sections
        secs = parse_sections(full_text)

        # upsert into DB (or create new)
        cv = db.query(ApplicationDetail).filter_by(resume_id=applicant_id).first()
        if not cv:
            cv = ApplicationDetail(resume_id=applicant_id, cv_file_name=filename)
            db.add(cv)

        cv.applicant_id = applicant_id
        cv.name         = name
        cv.job_history  = secs["job_history"]
        cv.education    = secs["education"]
        cv.skills       = secs["skills"]

        # you can also fill phone, birthdate, address with regex similarly

    db.commit()
    db.close()

if __name__ == "__main__":
    process_folder_and_update()
    print("PDF extraction & parsing complete!")
