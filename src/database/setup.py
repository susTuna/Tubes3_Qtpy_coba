import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import sys

load_dotenv()

def setup_db() -> bool:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ats_db")
    DB_PORT = os.getenv("DB_PORT", "3306")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            cursor.execute(f"USE {DB_NAME}")
            print(f"Database '{DB_NAME}' is ready.")

            cursor.close()
            conn.close()

            return True
    except Error as e:

        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("Setting up the database...")
    if setup_db():
        print("Database setup completed successfully.")
    else:
        print("Database setup failed.")
        sys.exit(1)