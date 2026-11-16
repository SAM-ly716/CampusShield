# CampusShield

CampusShield is a cybersecurity project using
Python Flask and SQLite.

## Requirements
- Python 3
- Flask
- SQLite

## Installation

1. Open the project folder:

   cd ~/campushield

2. Install Flask:

   python3 -m pip install -r requirements.txt

3. Create the database if it does not exist:

   sqlite3 campushield.db < schema.sql

4. Start the application:

   python3 app.py

5. Open the application:

   http://127.0.0.1:5000

## Security

This project is intended for testing inside
an isolated Kali Linux lab environment.
