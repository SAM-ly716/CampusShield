"""
CampusShield - basic portal GUI (optional demo front-end).

Standalone and additive: does not modify the lab baseline (app.py) or any Task
folder. Serves a simple login + student search page on port 5000 using the same
campushield.db, with parameterised queries so the GUI itself is injection-safe.

Run:  python gui_app.py   ->   http://127.0.0.1:5000
"""
from flask import Flask, request, session, redirect, render_template_string
import sqlite3

DatabasePath = "campushield.db"
PortalApp = Flask(__name__)
PortalApp.secret_key = "campushield-lab-demo"  # demo only; local isolated lab

# Simple demo logins: username -> (password, role)
DemoAccounts = {"admin": ("admin123", "admin"), "student1": ("student123", "student")}

# Same accounts as a list, so the sign-in page can display them as clickable cards.
DemoList = [{"username": userName, "password": creds[0], "role": creds[1]}
            for userName, creds in DemoAccounts.items()]


# Open a SQLite connection that returns rows keyed by column name.
def GetConnection():
    connection = sqlite3.connect(DatabasePath)
    connection.row_factory = sqlite3.Row
    return connection


# Look up students matching an optional name, using a parameterised LIKE query.
def FetchStudents(searchTerm):
    connection = GetConnection()
    # '?' placeholder keeps the input as data, so it can't change the query (SQLi-safe)
    query = "SELECT id,name,email,major,gpa FROM students WHERE name LIKE ? ORDER BY name"
    rows = connection.execute(query, ("%" + searchTerm + "%",)).fetchall()
    connection.close()
    return rows


# Fetch a single student by id (for the edit form), using a parameterised query.
def FetchOneStudent(studentId):
    connection = GetConnection()
    row = connection.execute(
        "SELECT id,name,email,major,gpa FROM students WHERE id=?", (studentId,)
    ).fetchone()
    connection.close()
    return row


PageHtml = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CampusShield</title>
<style>
  body { font-family:Segoe UI,Arial,sans-serif; background:#f4f6f8; color:#222; margin:0; }
  header { background:#0E7490; color:#fff; padding:14px 24px; font-size:18px; font-weight:700; }
  header span { float:right; font-size:13px; font-weight:400; color:#c9d6e5; }
  header a { color:#cffafe; text-decoration:none; margin-left:14px; font-size:13px; }
  .box { max-width:720px; margin:26px auto; background:#fff; border:1px solid #e2e6ea;
         border-radius:2px; padding:22px; }
  h2 { color:#0E7490; margin-top:0; }
  input { padding:9px 11px; border:1px solid #ccd3da; border-radius:2px; font-size:14px; }
  button { padding:9px 16px; background:#0E7490; color:#fff; border:0; border-radius:2px;
           font-size:14px; cursor:pointer; }
  table { width:100%; border-collapse:collapse; margin-top:14px; font-size:14px; }
  th { background:#f1f4f7; color:#0E7490; text-align:left; padding:9px; border-bottom:2px solid #e2e6ea; }
  td { padding:9px; border-bottom:1px solid #eef1f4; }
  .err { color:#9b2c22; font-size:13px; margin-top:8px; }
  .hint { color:#667; font-size:12px; margin-top:12px; }
  button.del { background:#b91c1c; padding:6px 11px; font-size:13px; }
  a.editbtn { display:inline-block; background:#0E7490; color:#fff; text-decoration:none;
              padding:6px 11px; border-radius:2px; font-size:13px; margin-right:6px; }
  .addform input { margin:0 6px 6px 0; }
  .addform { margin-top:6px; }
  .accts { margin-top:18px; border-top:1px solid #eef1f4; padding-top:14px; }
  .accts .lbl { font-size:12px; color:#667; margin-bottom:8px; font-weight:600; }
  button.acct { display:block; width:100%; text-align:left; background:#ecf6f8; color:#0E7490;
                border:1px solid #cfe6ec; border-radius:2px; margin-bottom:8px; padding:11px 13px;
                font-weight:600; font-size:14px; }
  button.acct span { float:right; color:#667; font-weight:400; font-size:12px; }
</style></head><body>
<header>CampusShield
  {% if user %}<span>{{ user }} ({{ role }}) <a href="/logout">sign out</a></span>{% endif %}
</header>
<div class="box">
{% if not user %}
  <h2>Sign in</h2>
  <form method="post" action="/login">
    <input type="text" name="username" placeholder="username" autocomplete="off">
    <input type="password" name="password" placeholder="password" autocomplete="off">
    <button type="submit">Sign in</button>
  </form>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <div class="accts">
    <div class="lbl">Demo logins &mdash; click an account to sign in</div>
    {% for a in accounts %}
      <form method="post" action="/login">
        <input type="hidden" name="username" value="{{ a.username }}">
        <input type="hidden" name="password" value="{{ a.password }}">
        <button class="acct" type="submit">{{ a.username }} / {{ a.password }} <span>{{ a.role }}</span></button>
      </form>
    {% endfor %}
  </div>
{% else %}{% if editing %}
  <h2>Edit student</h2>
  <form method="post" action="/edit" class="addform">
    <input type="hidden" name="id" value="{{ editing['id'] }}">
    <input type="text" name="name" value="{{ editing['name'] }}" placeholder="name" required>
    <input type="text" name="major" value="{{ editing['major'] }}" placeholder="major" style="width:90px">
    <input type="text" name="email" value="{{ editing['email'] }}" placeholder="email">
    <input type="text" name="gpa" value="{{ editing_gpa }}" placeholder="GPA" style="width:70px">
    <button type="submit">Save</button>
    <a href="/" style="margin-left:10px;color:#667;font-size:13px">Cancel</a>
  </form>
{% else %}
  <h2>Student records</h2>
  <form method="get" action="/">
    <input type="text" name="q" placeholder="search by name" value="{{ query }}" style="width:70%">
    <button type="submit">Search</button>
  </form>
  <table>
    <tr><th>Name</th><th>Major</th>
      {% if full %}<th>Email</th><th>GPA</th><th></th>{% endif %}</tr>
    {% for s in students %}
      <tr><td>{{ s['name'] }}</td><td>{{ s['major'] }}</td>
        {% if full %}<td>{{ s['email'] }}</td>
          <td>{% if s['gpa'] is not none %}{{ '%.1f'|format(s['gpa']) }}{% endif %}</td>
          <td><a class="editbtn" href="/edit?id={{ s['id'] }}">Edit</a>
            <form method="post" action="/delete" style="display:inline;margin:0"
                onsubmit="return confirm('Delete {{ s['name'] }}?')">
            <input type="hidden" name="id" value="{{ s['id'] }}">
            <button type="submit" class="del">Delete</button></form></td>{% endif %}
      </tr>
    {% endfor %}
  </table>
  {% if not students %}<div class="hint">No matches for "{{ query }}".</div>{% endif %}
  {% if full %}
    <h2 style="margin-top:22px;font-size:17px">Add a student</h2>
    <form method="post" action="/add" class="addform">
      <input type="text" name="name" placeholder="name" required>
      <input type="text" name="major" placeholder="major" style="width:90px">
      <input type="text" name="email" placeholder="email">
      <input type="text" name="gpa" placeholder="GPA" style="width:70px">
      <button type="submit">Add</button>
    </form>
  {% else %}
    <div class="hint">Student view: email and GPA hidden (role-based access).</div>
  {% endif %}
{% endif %}{% endif %}
</div></body></html>
"""


# Home: shows the login form, or the search page once signed in.
@PortalApp.route("/")
def Home():
    currentUser = session.get("user")
    if not currentUser:
        return render_template_string(PageHtml, user=None, error=None, query="", accounts=DemoList)
    searchTerm = request.args.get("q", "").strip()
    students = FetchStudents(searchTerm)
    # admin sees full records; a student gets a reduced, least-privilege view
    showFull = currentUser["role"] == "admin"
    return render_template_string(PageHtml, user=currentUser["name"], role=currentUser["role"],
                                  students=students, query=searchTerm, full=showFull)


# Check the demo credentials and start a session.
@PortalApp.route("/login", methods=["POST"])
def Login():
    userName = request.form.get("username", "")
    plainPassword = request.form.get("password", "")
    account = DemoAccounts.get(userName)
    if account and account[0] == plainPassword:
        session["user"] = {"name": userName, "role": account[1]}
        return redirect("/")
    return render_template_string(PageHtml, user=None, error="Invalid username or password.",
                                  query="", accounts=DemoList)


# Add a new student record (admin only), using a parameterised INSERT.
@PortalApp.route("/add", methods=["POST"])
def AddStudent():
    currentUser = session.get("user")
    # role check: only an admin may modify records (least privilege)
    if not currentUser or currentUser["role"] != "admin":
        return redirect("/")
    studentName = request.form.get("name", "").strip()
    studentMajor = request.form.get("major", "").strip()
    studentEmail = request.form.get("email", "").strip()
    gpaText = request.form.get("gpa", "").strip()
    # a blank or non-numeric GPA is stored as NULL rather than crashing the insert
    try:
        gpaValue = float(gpaText) if gpaText else None
    except ValueError:
        gpaValue = None
    if studentName:
        connection = GetConnection()
        connection.execute(
            "INSERT INTO students (name,email,dob,major,gpa) VALUES (?,?,?,?,?)",
            (studentName, studentEmail, "", studentMajor, gpaValue))
        connection.commit()
        connection.close()
    return redirect("/")


# Delete a student record by id (admin only), using a parameterised DELETE.
@PortalApp.route("/delete", methods=["POST"])
def DeleteStudent():
    currentUser = session.get("user")
    if not currentUser or currentUser["role"] != "admin":
        return redirect("/")
    studentId = request.form.get("id", "")
    if studentId:
        connection = GetConnection()
        connection.execute("DELETE FROM students WHERE id=?", (studentId,))
        connection.commit()
        connection.close()
    return redirect("/")


# Show a prefilled edit form for one student (admin only).
@PortalApp.route("/edit", methods=["GET"])
def EditForm():
    currentUser = session.get("user")
    if not currentUser or currentUser["role"] != "admin":
        return redirect("/")
    studentRow = FetchOneStudent(request.args.get("id", ""))
    if not studentRow:
        return redirect("/")
    # show the GPA as text so the number (or a blank) prefills the field cleanly
    gpaText = "" if studentRow["gpa"] is None else ("%.1f" % studentRow["gpa"])
    return render_template_string(PageHtml, user=currentUser["name"], role=currentUser["role"],
                                  editing=studentRow, editing_gpa=gpaText)


# Save edits to a student record (admin only), using a parameterised UPDATE.
@PortalApp.route("/edit", methods=["POST"])
def EditStudent():
    currentUser = session.get("user")
    if not currentUser or currentUser["role"] != "admin":
        return redirect("/")
    studentId = request.form.get("id", "")
    studentName = request.form.get("name", "").strip()
    studentMajor = request.form.get("major", "").strip()
    studentEmail = request.form.get("email", "").strip()
    gpaText = request.form.get("gpa", "").strip()
    try:
        gpaValue = float(gpaText) if gpaText else None
    except ValueError:
        gpaValue = None
    if studentId and studentName:
        connection = GetConnection()
        connection.execute("UPDATE students SET name=?, email=?, major=?, gpa=? WHERE id=?",
                           (studentName, studentEmail, studentMajor, gpaValue, studentId))
        connection.commit()
        connection.close()
    return redirect("/")


# Clear the session.
@PortalApp.route("/logout")
def Logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    PortalApp.run(host="127.0.0.1", port=5000)
