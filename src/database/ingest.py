import kagglehub
from datetime import datetime, timedelta
import random
from faker import Faker
from kagglehub import KaggleDatasetAdapter
from models import ApplicationDetail, ApplicantProfile, SessionLocal, init_db

fake = Faker()

def load_kaggle():
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "snehaanbhawal/resume-dataset",
        "kaggle.json",
        pandas_kwargs={"encoding": "utf-8"}
    )
    return df

def generate_random_date(start_year=1980, end_year=2002):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_days)

def seed_from_csv():
    init_db()
    df = load_kaggle()

    db = SessionLocal()

    applicant_map = {}

    print("Seeding Applicant Profiles...")
    for i in range(random.randint(50, 100)):
        profile = ApplicantProfile(
            first_name = fake.first_name(),
            last_name  = fake.last_name(),
            birthdate  = generate_random_date(),
            address    = fake.address().replace('\n', ', '),
            phone      = fake.phone_number()
        )

        db.add(profile)
        db.flush()

        applicant_map[i] = profile.applicant_id
    
    db.commit()
    print(f"Created {len(applicant_map)} applicant profiles.")

    print("Seeding Application Details...")
    for i, (_, row) in enumerate(df.iterrows()):

        r = ApplicationDetail(
            applicant_id = applicant_map[random.randint(0, len(applicant_map) - 1)],
            applicant_role = row["Category"],
            cv_file_name = row["ID"]
        )
        db.add(r)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_from_csv()
    print("Database seeded!")
