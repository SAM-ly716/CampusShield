
import hashlib
import hmac
import os

# Synthetic account for the CampusShield lab
username = "student01"
password = "Campus@2026!"
salt = os.urandom(16)
stored_hash = hashlib.pbkdf2_hmac(
    "sha256", password.encode(), salt, 200000
)

failed_attempts = 0
max_attempts = 5

print("=== CampusShield Authentication Demo ===")

while True:
    if failed_attempts >= max_attempts:
        print("ACCOUNT LOCKED: Too many failed attempts.")
        break

    user = input("Username: ")
    pw = input("Password: ")

    attempted_hash = hashlib.pbkdf2_hmac(
        "sha256", pw.encode(), salt, 200000
    )

    if user == username and hmac.compare_digest(
        attempted_hash, stored_hash
    ):
        print("LOGIN SUCCESSFUL")
        break
    else:
        failed_attempts += 1
        print(f"LOGIN FAILED ({failed_attempts}/5)")
