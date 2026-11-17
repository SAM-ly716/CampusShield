
import hashlib
import hmac
import os

def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return salt.hex() + ":" + hashed.hex()

def verify_password(stored, password):
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)

    actual = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return hmac.compare_digest(actual, expected)

password = "Campus@2026!"

stored1 = hash_password(password)
stored2 = hash_password(password)

print("=== CampusShield Secure Password Hashing ===")
print("User 1 Salted Hash:", stored1)
print("User 2 Salted Hash:", stored2)
print("Different hashes:", stored1 != stored2)
print("Correct password:", verify_password(stored1, password))
print("Wrong password:", verify_password(stored1, "wrong123"))
