import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter
from models import Resume, SessionLocal, init_db

def load_kaggle():
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "snehaanbhawal/resume-dataset",
        "kaggle.json",
        pandas_kwargs={"encoding": "utf-8"}
    )
    return df

def seed_from_csv():
    init_db()
    df = load_kaggle()

    db = SessionLocal()
    for _, row in df.iterrows():
        r = Resume(
            resume_id    = row['file_name'],       # adjust to actual column
            resume_str   = row['resume_text'],     # adjust to actual column
            resume_html  = row['resume_html'],     # adjust to actual column
            category     = row['category'],
            cv_file_name = row['file_name'],       # assume the PDFs are named same
        )
        db.add(r)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_from_csv()
    print("✅ Database seeded!")
