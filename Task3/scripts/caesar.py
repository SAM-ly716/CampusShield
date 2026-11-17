
def caesar(text, shift):
    result = ""
    for char in text:
        if char.isalpha() and char.isascii():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

message = "CAMPUSSHIELD STUDENT DATA"
shift = 3

encrypted = caesar(message, shift)
decrypted = caesar(encrypted, -shift)

print("=== CampusShield Caesar Cipher Demo ===")
print("Original message:", message)
print("Shift key:", shift)
print("Encrypted message:", encrypted)
print("Decrypted message:", decrypted)

print("\n=== Brute Force: All 25 Shifts ===")
for key in range(1, 26):
    print(f"Shift {key:2}: {caesar(encrypted, -key)}")
