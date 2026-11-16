from flask import Flask, request, g
import sqlite3

app = Flask(__name__)
DB = "campushield.db"

def db():
    if "db" not in g: g.db = sqlite3.connect(DB)
    return g.db

# VULNERABLE login: string-concatenated SQL -> SQL injection
@app.route("/login")
def login():
    u = request.args.get("user", "")
    p = request.args.get("pw", "")
    q = "SELECT * FROM users WHERE username='%s' AND pw_hash='%s'" % (u, p)
    row = db().execute(q).fetchone()
    return "WELCOME " + str(row) if row else "DENIED"

# VULNERABLE search: reflects raw input -> reflected XSS, no escaping
@app.route("/search")
def search():
    name = request.args.get("name", "")
    rows = db().execute(
        "SELECT name,email FROM students WHERE name LIKE '%" + name + "%'"
    ).fetchall()
    return "<h3>Results for " + name + "</h3>" + str(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)   # binds to ALL interfaces = exposed
