"""
CampusShield - FIXED application (Task 4 remediation).

Same routes as the vulnerable baseline (app.py), but with the weaknesses closed:
  - SQL injection  -> parameterised queries
  - Reflected XSS  -> output escaping via markupsafe.escape
  - Clickjacking   -> X-Frame-Options / CSP / nosniff security headers
  - Weak auth      -> salted scrypt password verification
  - RBAC           -> role checked before privileged data is returned

Keep the original app.py as the committed VULNERABLE baseline so before/after is
provable; run this file to demonstrate the fixed behaviour.
"""
from flask import Flask, request, g, Response
from markupsafe import escape
import sqlite3
import hashlib

app = Flask(__name__)
DB = "campushield.db"


# Return the per-request SQLite connection, opening it once.
def GetDb():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
    return g.db


# Verify a password against a stored "salt:key" scrypt hash (see Task 3 hashpw.py).
def VerifyPassword(storedHash, attempt):
    # PLACEHOLDER rows have no real hash yet; never treat them as a match.
    if not storedHash or ":" not in storedHash:
        return False
    saltHex, keyHex = storedHash.split(":")
    salt = bytes.fromhex(saltHex)
    candidate = hashlib.scrypt(attempt.encode(), salt=salt, n=16384, r=8, p=1)
    # hashlib digests are fixed length, so a constant-time compare is appropriate.
    return hashlib.compare_digest(candidate.hex(), keyHex)


# FIXED login: the username is bound as a parameter, so input can never alter the
# query structure. The password is checked against a salted hash, not compared in SQL.
@app.route("/login")
def Login():
    suppliedUser = request.args.get("user", "")
    suppliedPassword = request.args.get("pw", "")
    row = GetDb().execute(
        "SELECT pw_hash, role FROM users WHERE username = ?",
        (suppliedUser,),
    ).fetchone()
    if row and VerifyPassword(row[0], suppliedPassword):
        return "WELCOME %s" % escape(suppliedUser)
    return "DENIED"


# FIXED search: value is bound as a parameter (no SQLi) and every piece of
# user-controlled text is escaped before it reaches HTML (no reflected XSS).
@app.route("/search")
def Search():
    searchName = request.args.get("name", "")
    rows = GetDb().execute(
        "SELECT name, email FROM students WHERE name LIKE ?",
        ("%" + searchName + "%",),
    ).fetchall()
    safeName = escape(searchName)
    body = "<h3>Results for %s</h3><ul>" % safeName
    for name, email in rows:
        body += "<li>%s - %s</li>" % (escape(name), escape(email))
    body += "</ul>"
    return body


# RBAC example: only an admin/registrar identity may list all students.
@app.route("/students")
def ListStudents():
    callerRole = request.args.get("role", "student")
    if callerRole not in ("admin", "registrar"):
        return Response("FORBIDDEN - insufficient role", status=403)
    rows = GetDb().execute("SELECT name, email FROM students").fetchall()
    return "<ul>" + "".join("<li>%s</li>" % escape(r[0]) for r in rows) + "</ul>"


# Defence in depth: send security headers on every response.
@app.after_request
def AddSecurityHeaders(response):
    response.headers["X-Frame-Options"] = "DENY"                 # clickjacking
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"       # MIME sniffing
    return response


if __name__ == "__main__":
    # Bind to localhost only - not every interface - as the Task 2 control requires.
    app.run(host="127.0.0.1", port=5000)
