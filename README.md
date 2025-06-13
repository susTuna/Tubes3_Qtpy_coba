### Setup Environment
1. Create a `.env` file in the project root
```bash
DB_USER = your_mysql_username
DB_PASSWORD = your_mysql_password
DB_HOST = localhost
DB_PORT = 3306
DB_NAME = ats_db
CV_FOLDER = ./data
KAGGLE_USERNAME = your_kaggle_username
KAGGLE_KEY = your_kaggle_api_key
```
2. Create the MySQL database
```bash
mysql -u root -p
```
    Then in the MySQL prompt:
```sql
CREATE DATABASE ats_db;
EXIT;
```

3. Import SQL Dump
```bash
mysql -u <DB_USER> -p <DB_PASSWORD> ats_db < path/to/dump.sql