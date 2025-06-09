import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.database.ingest import seed_from_csv
from src.database.models import init_db
from src.database.setup import setup_db

def setup():
    print("Setting up the database...")
    if setup_db():
        print("Database setup completed successfully.")
    else:
        print("Database setup failed.")
        exit(1)

def init():
    print("Initializing the database...")
    if init_db():
        print("Database initialized successfully.")
    else:
        print("Database initialization failed.")
        exit(1)
    
def seed():
    print("Seeding the database with sample data...")
    if seed_from_csv():
        print("Database seeded successfully.")
    else:
        print("Database seeding failed.")
        exit(1)

if __name__ == "__main__":
    setup()
    init()
    seed()
    print("Database setup, initialization, and seeding complete!")

