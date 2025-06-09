import os
from dotenv import load_dotenv

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