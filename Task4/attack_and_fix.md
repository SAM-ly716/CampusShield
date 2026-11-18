# Task 4 - Attack, Fix, Retest (SQL injection + reflected XSS + clickjacking)

Loop for every test: baseline attack -> evidence -> apply fix -> repeat same test ->
quantify. Screenshots to capture are named at each step.

## A. SQL injection on /login

### Baseline (against the VULNERABLE app.py)
    python3 app.py            # the vulnerable baseline
    curl "http://localhost:5000/login?user=admin'--&pw=wrongpass"

**What the input changes:** `admin'--` closes the username string and comments out the
rest of the WHERE clause, so the password check is removed entirely.
**Unauthorised result:** the query returns the admin row and the app responds
`WELCOME ...` even though the password is wrong -> authentication bypass.
-> screenshot: `evidence/T4_01_SQLi_Baseline_Bypass.png`

### Fix
Parameterised query - the username is bound, never concatenated, so input cannot
change the query structure (see `app_fixed.py` `Login`).

### Retest (against app_fixed.py)
    python3 app_fixed.py
    curl "http://localhost:5000/login?user=admin'--&pw=wrongpass"   # -> DENIED
    # and a correct login still works once hashes are seeded (Task 3):
    curl "http://localhost:5000/login?user=admin&pw=<correct-pass>" # -> WELCOME admin
**Result:** the injection now returns `DENIED`; normal login still succeeds.
-> screenshot: `evidence/T4_02_SQLi_Blocked.png`

## B. Reflected XSS on /search

### Baseline
    curl "http://localhost:5000/search?name=<script>alert(1)</script>"
**Precondition:** a victim must open an attacker-crafted link, and the browser must
render the reflected markup. The vulnerable app returns the raw `<script>` unescaped.
-> screenshot: `evidence/T4_03_XSS_Baseline.png` (open the URL in a browser to show the alert)

### Fix
`markupsafe.escape()` on all user text (see `app_fixed.py` `Search`).

### Retest
    curl "http://localhost:5000/search?name=<script>alert(1)</script>"
**Result:** the response now contains `&lt;script&gt;alert(1)&lt;/script&gt;` - the
tag is shown as text, not executed.
-> screenshot: `evidence/T4_04_XSS_Blocked.png`

## C. Clickjacking (missing frame protection)

### Baseline
    curl -I "http://localhost:5000/search?name=x"      # no X-Frame-Options header
**Precondition:** the app can be loaded inside an attacker's hidden `<iframe>` and
overlaid to trick clicks.
-> screenshot: `evidence/T4_05_NoFrameHeader.png`

### Fix + retest
    curl -I "http://localhost:5000/search?name=x"      # now shows X-Frame-Options: DENY
**Result:** `X-Frame-Options: DENY`, `Content-Security-Policy`, and
`X-Content-Type-Options: nosniff` are present -> framing blocked.
-> screenshot: `evidence/T4_06_FrameHeader_Fixed.png`

## D. Why input validation is NOT a substitute for parameterised SQL
Validation is a filter (e.g. "reject quotes") that attackers bypass with encoding,
alternate syntax, or edge cases it did not anticipate. Parameterised queries make the
input **data, never executable SQL** - the database treats it as a value regardless of
its content. Validation is a useful *extra* layer, not the fix.

## E. Reachability from an unauthorised zone (reuse Task 2)
Using the Task 2 firewall/binding result: after binding the app to 127.0.0.1 and the
ufw rule, re-run the nmap scan from a second VM - port 5000 is **filtered**, so the
attack surface is unreachable from an unauthorised lab zone even before the code fixes.
Together (network control + code fix) this is defence in depth.

## F. Severity / residual risk (do NOT claim "completely secure")
- SQL injection: **was Critical** (full auth bypass) -> **mitigated** by parameterisation.
- Reflected XSS: **was High** -> **mitigated** by output escaping.
- Clickjacking: **was Medium** -> **mitigated** by headers.
- **Residual risk (Low-Medium):** unpatched dependencies, no HTTPS/TLS yet (credentials
  still travel in clear - see Wireshark note), and no rate limiting on /search. These
  remain for a future iteration.
