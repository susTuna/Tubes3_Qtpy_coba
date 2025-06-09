import pandas as pd
import io
import os
from datetime import datetime, timedelta
import random
from faker import Faker
from .models import ApplicationDetail, ApplicantProfile, SessionLocal
from ..config.config import KAGGLE_USER, KAGGLE_KEY

fake = Faker()

def load_kaggle():
    """Load Kaggle dataset directly into memory without downloading files to disk"""
    # Initialize the Kaggle API
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USER
    print(f"KAGGLE_USERNAME set to: {KAGGLE_USER}")
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY
    print(f"KAGGLE_KEY set to: {KAGGLE_KEY}")

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    
    # Get dataset file list
    files = api.dataset_list_files("snehaanbhawal/resume-dataset").files
    
    # Find the CSV file
    csv_file = next((f.name for f in files if f.name.endswith('.csv')), None)
    
    if not csv_file:
        raise FileNotFoundError("No CSV file found in the dataset")
    
    # Get the file content directly
    response = api.dataset_download_file(
        dataset="snehaanbhawal/resume-dataset", 
        file_name=csv_file,
        quiet=False
    )
    
    # Load directly into pandas from memory
    df = pd.read_csv(io.StringIO(response.text), encoding='utf-8')
    print(f"Loaded {len(df)} records directly from Kaggle")
    
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
                        birthdate  = generate_random_date(),
                        address    = fake.address().replace('\n', ', '),
                        phone      = fake.phone_number()
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
                        applicant_role = row["Category"],
                        cv_file_name = row["ID"]
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
