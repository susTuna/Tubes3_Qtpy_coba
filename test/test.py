import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.database.ingest import seed_from_csv
from src.database.models import init_db, dump_db
from src.database.setup import setup_db
from src.database.parser import parse_for_regex, parse_text
from src.database.pdf_utils import extract_text_from_pdf
from src.config.config import DB_PATH

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

def dump():
    DB_SCHEMA = f"{DB_PATH}/tubes3_schema.sql"
    DB_FILE   = f"{DB_PATH}/tubes3.sql"
    print("Exporting the database to a SQL file...")
    if dump_db(DB_SCHEMA) and dump_db(DB_FILE, False):
        print("Database exported successfully.")
    else:
        print("Database export failed.")
        exit(1)

def parse():
    text = extract_text_from_pdf("data/10276858.pdf")

    regex = parse_for_regex(text)
    print("Parsed text with regex:")
    for line in regex:
        print(line)
    print("\n Parsed text: ")
    parsed_text = parse_text(text)
    print(parsed_text)

if __name__ == "__main__":
    # setup()
    # init()
    # seed()
    # dump()
    # print("Database setup, initialization, and seeding complete!")
    parse()
