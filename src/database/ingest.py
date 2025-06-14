import pandas as pd
import kagglehub
import os
from datetime import datetime, timedelta
import random
from faker import Faker
from .models import ApplicationDetail, ApplicantProfile, SessionLocal
from ..config.config import KAGGLE_USER, KAGGLE_KEY

fake = Faker('id_ID')

def load_kaggle():
    """Load Kaggle dataset with caching to avoid redownloading"""
    print("Loading data from Kaggle...")
    
    # Define the known path to the CSV file
    home_dir = os.path.expanduser("~")
    cached_csv_path = os.path.join(home_dir, ".cache/kagglehub/datasets/snehaanbhawal/resume-dataset/versions/1/Resume/Resume.csv")
    
    # Check if the CSV file already exists
    if os.path.exists(cached_csv_path):
        print(f"Using cached file: {cached_csv_path}")
        df = pd.read_csv(cached_csv_path)
        print(f"Loaded {len(df)} records from cached file")
        return df
    
    # If not found, download from Kaggle
    print("Cached file not found. Downloading from Kaggle...")
    path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
    print(f"Dataset downloaded to: {path}")
    
    # Find CSV files in the downloaded path
    csv_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {path}")
    
    # Load the first CSV file found
    csv_path = csv_files[0]
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from {os.path.basename(csv_path)}")
    
    return df

def generate_random_date(start_year=1980, end_year=2002):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_days)

def seed_from_csv():
    try:
        print("Loading data from Kaggle...")
        try:
            df = load_kaggle()
        except Exception as e:
            print(f"Failed to load data from Kaggle: {str(e)}")
            return False
        
        db = None
        try:
            db = SessionLocal()
        except Exception as e:
            print(f"Failed to create database session: {str(e)}")
            return False

        applicant_map = {}

        try:
            print("Seeding Applicant Profiles...")
            profile_count = random.randint(50, 100)
            for i in range(profile_count):
                try:
                    profile = ApplicantProfile(
                        first_name = fake.first_name(),
                        last_name  = fake.last_name(),
                        date_of_birth = generate_random_date(),
                        address    = fake.address().replace('\n', ', '),
                        phone_number = fake.numerify(text="+62-8##-####-####")
                    )
                    
                    db.add(profile)
                    db.flush()
                    
                    applicant_map[i] = profile.applicant_id
                except Exception as e:
                    print(f"Error creating profile {i+1}/{profile_count}: {str(e)}")
                    
            db.commit()
            print(f"Created {len(applicant_map)} applicant profiles.")
            
            if len(applicant_map) == 0:
                print("No applicant profiles were created. Cannot continue.")
                return False
                
            print("Seeding Application Details...")
            application_count = 0
            for i, (_, row) in enumerate(df.iterrows()):
                try:
                    r = ApplicationDetail(
                        applicant_id = applicant_map[random.randint(0, len(applicant_map) - 1)],
                        application_role = row["Category"],
                        cv_path = row["ID"]
                    )
                    db.add(r)
                    application_count += 1
                except Exception as e:
                    print(f"Error creating application {i+1}/{len(df)}: {str(e)}")
            
            db.commit()
            print(f"Created {application_count} application details.")
            
            return True
            
        except Exception as e:
            print(f"An unexpected error occurred during database seeding: {str(e)}")

            if db:
                db.rollback()
            return False
        
    finally:
        if 'db' in locals() and db:
            db.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting database seeding...")
    if seed_from_csv():
        print("Database successfully seeded!")
    else:
        print("Database seeding failed")
