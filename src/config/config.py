import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "3306"),
    "database": os.getenv("DB_NAME", "ats_db"),
}

DB_CONN = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
          f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

CV_FOLDER = os.path.join(PROJECT_ROOT, "./data")

KAGGLE_USER = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")

DB_PATH = os.path.join(PROJECT_ROOT, "./src/database")

ENCRYPTION_PASSWORD = os.getenv("ENCRYPT_PASSWORD", "admin")