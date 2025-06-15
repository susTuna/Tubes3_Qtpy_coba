# Applicant Tracking System

<div align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&height=300&color=timeGradient&text=Qtpy%20Coba&reversal=true&fontColor=ffffff&animation=twinkling&stroke=fffffff&strokeWidth=4&fontSize=0" />
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Done-008000" />
  <img src="https://img.shields.io/badge/Version-1.0.0-brightgreen" />
  <img src="https://img.shields.io/badge/License-MIT-yellowgreen" />
  <img src="https://img.shields.io/badge/Built_With-Python-blue" />
</p>

<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=500&color=81a1c1&center=true&vCenter=true&width=600&lines=13523123,+13523146,+and+13523147;Bimo,+El,+dan+Rik" alt="R.Bimo, Rafael, dan Frederiko" />
</h1>

## 📦 Table of Contents

  - [🔍 Overview](#-overview)
  - [📶 How To Run](#-how-to-run)
  - [⚙️ Configuration](#️-configuration)
  - [🤖 Technologies & Algorithms](#-technologies--algorithms)
  - [👤 Author](#-author)
  - [♾️ License](#️-license)

-----

## 🔍 Overview

This application serves as an **Applicant Tracking System (ATS)** designed for efficient management and searching of CVs. It leverages advanced string matching algorithms to provide fast and accurate search capabilities, allowing users to find relevant CVs based on keywords. The system also includes robust data encryption for sensitive applicant information.

### Fitur

  * **Advanced CV Search**: Utilize various string matching algorithms (KMP, Boyer-Moore Simple, Boyer-Moore Complex, Aho-Corasick, and Fuzzy Search) to find keywords within CV documents.
  * **Data Preprocessing**: Efficiently extracts and caches text from PDF CVs for faster subsequent searches.
  * **Data Encryption**: Sensitive applicant information (names, addresses, phone numbers, and CV paths) is encrypted using a custom Cellular Automata Encryption (CAE) system for enhanced security.
  * **Detailed CV Summaries**: View parsed information like skills, professional experience, and educational background from extracted CV content.
  * **Interactive GUI**: A user-friendly interface built with PyQt6 for seamless interaction, search configuration, and results display.
  * **Database Integration**: Stores applicant profiles and application details using SQLAlchemy and a MySQL database.

-----

## 📶 How To Run

Follow these steps to get the application running on your local machine:

Note: Please have Python 3.11+ installed.

0.  **Install `uv` (recommended package installer)**

      * Windows:
        ```powershell
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
      * MacOS and Linux:
        With `curl`:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
        With `wget`:
        ```bash
        wget -qO- https://astral.sh/uv/install.sh | sh
        ```
      * Alternatively, see detailed installation steps [here](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1).

1.  **Download the ZIP Release**

      * Navigate to the repository’s releases page and download the latest zip file.

2.  **Extract the ZIP File**

      * Unzip the downloaded file to your preferred location.

3.  **Navigate to the Project Directory**

      * Open your terminal or command prompt and change the directory to the extracted project folder:
        ```bash
        cd path/to/your/extracted/folder
        ```

4.  **Run the Application**

      * Execute the `main.py` file directly:
        ```bash
        uv run main.py
        ```
      * The PyQt6 GUI window will open, and the application will start.

-----

## ⚙️ Configuration

1.  **Create a `.env` file** in the project root with the following variables:

    ```bash
    DB_USER = your_mysql_username
    DB_PASSWORD = your_mysql_password
    DB_HOST = localhost
    DB_PORT = 3306
    DB_NAME = ats_db
    CV_FOLDER = ./data
    KAGGLE_USERNAME = your_kaggle_username
    KAGGLE_KEY = your_kaggle_api_key
    ENCRYPT_PASSWORD = your_encryption_password
    ```

      * `CV_FOLDER`: Specifies where your CV PDF files are located. Default is `./data`.
      * `KAGGLE_USERNAME` and `KAGGLE_KEY`: Required for seeding the database with dummy data if you choose to use the `ingest.py` script.
      * `ENCRYPT_PASSWORD`: The password used for encrypting and decrypting sensitive data in the database.

2.  **Create the MySQL database**:

    ```bash
    mysql -u root -p
    ```

    Then, in the MySQL prompt:

    ```sql
    CREATE DATABASE ats_db;
    EXIT;
    ```

3.  **Import SQL Dump** (optional, for pre-seeded data):
    You can import the provided `tubes3.sql` file to populate the database with sample data:

    ```bash
    mysql -u <DB_USER> -p <DB_PASSWORD> ats_db < src/database/tubes3.sql
    ```

    Replace `<DB_USER>` and `<DB_PASSWORD>` with your MySQL credentials from the `.env` file.

-----

## 🤖 Technologies & Algorithms

  * **Backend & Logic**: Python
      * **Database**: SQLAlchemy with PyMySQL connector for MySQL.
      * **PDF Processing**: `PyPDF2` for text extraction.
      * **Data Ingestion**: `pandas` and `kagglehub` for loading and seeding data.
      * **Concurrency**: `concurrent.futures.ThreadPoolExecutor` for parallel processing of CVs.
      * **Encryption**: Custom Cellular Automata Encryption (CAE) for secure data handling.
  * **String Matching Algorithms**:
      * **Exact Matching**:
          * **KMP (Knuth-Morris-Pratt)**: Efficient for single pattern matching with linear time complexity.
          * **Boyer-Moore**: Uses bad character and good suffix heuristics for fast pattern matching.
          * **Aho-Corasick**: Optimal for multiple pattern matching, finds all patterns simultaneously.
      * **Fuzzy Search**: Finds approximate matches using edit distance (Levenshtein distance), great for typos and variations.
  * **Frontend**: PyQt6 for the graphical user interface.

-----

## 👤 Author

<table align="center">
  <tr>
    <th align="center">User</th>
    <th align="center">Job</th>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/Cola1000">
        <img src="https://avatars.githubusercontent.com/u/143616767?v=4" width="80px" style="border-radius: 50%;" alt="Cola1000"/><br />
        <sub><b>Rhio Bimo Prakoso S</b></sub>
      </a>
    </td>
    <td align="center">Database, Service, dan Testing</td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/V-Kleio">
        <img src="https://avatars.githubusercontent.com/u/101655336?v=4" width="80px" style="border-radius: 50%;" alt="V-Kleio"/><br />
        <sub><b>Rafael Marchel Dharma Wijaya</b></sub>
      </a>
    </td>
    <td align="center">GUI, Search Algorithm, dan Encryption</td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/susTuna">
        <img src="https://avatars.githubusercontent.com/u/148179846?s=96&v=4" width="80px" style="border-radius: 50%;" alt="susTuna"/><br />
        <sub><b>Frederiko Eldad Mugiyono</b></sub>
      </a>
    </td>
    <td align="center">GUI, Database Migration, Service dan Finishing</td>
  </tr>
</table>

<div align="center" style="color:#6A994E;"> 🌿 Please Donate for Charity! 🌿</div>

<p align="center">
  <a href="https://tiltify.com/@cdawg-va/cdawgva-cyclethon-4" target="_blank">
    <img src="https://assets.tiltify.com/uploads/cause/avatar/4569/blob-9169ab7d-a78f-4373-8601-d1999ede3a8d.png" alt="IDF" style="height: 80px;padding: 20px" />
  </a>
</p>

-----

## ♾️ License

This project is licensed under the [MIT License](https://www.google.com/search?q=https://github.com/Cola1000/Applicant-Tracking-System/blob/main/LICENSE)
