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

## Task 4 - Application and Database Weaknesses

Task 4 demonstrates and fixes three web/database weaknesses, each following a
baseline -> fix -> retest loop.

Weaknesses (baseline in app.py):
- SQL injection on /login - user=admin'-- bypasses authentication.
- Reflected XSS on /search - unescaped input is rendered back in the response.
- Clickjacking - no X-Frame-Options header, so the page can be framed.

Fixes (Task4/app_fixed.py):
- Parameterised queries (SQLi), output escaping with markupsafe (XSS),
  security headers X-Frame-Options / CSP / nosniff (clickjacking), salted scrypt
  password verification, and an RBAC role check.

Files:
- Task4/app_fixed.py - remediated application
- Task4/attack_and_fix.md - baseline attacks, mitigations, retest, severity and residual risk
- Task4/phishing_sample.eml and Task4/phishing_analysis.md - phishing/spoofing simulation

Quick test:

   # baseline (vulnerable)
   python3 app.py &
   curl "http://localhost:5000/login?user=admin'--&pw=x"      # bypass -> WELCOME

   # after fix
   python3 Task4/app_fixed.py &
   curl "http://localhost:5000/login?user=admin'--&pw=x"      # blocked -> DENIED

## Task 5 (Q3) - Logging and Brute-Force Detection

Task 5 Q3 provides log monitoring: a script that parses an authentication log and
alerts on repeated failed logins from a single source (brute-force detection).

Files:
- Task5/log_monitor.py - generates a synthetic auth log, parses it, and alerts on any
  source IP with failed logins above the threshold (5).
- Task5/log_monitor_output.txt - captured output (alert for 10.0.0.66).

Run:

   python3 Task5/log_monitor.py

## Security

This project is intended for testing inside
an isolated Kali Linux lab environment.
