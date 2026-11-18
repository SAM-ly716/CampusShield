# Task 4 - Phishing / Email-Spoofing Simulation (local only)

A simulated credential-phishing email is provided in `phishing_sample.eml`. Nothing is
sent - it is a sample for analysis only.

## Red flags in the sample
1. **Lookalike sender domain** - `campus-shield-helpdesk.test`, not the real
   university domain. Spoofed display name "IT Support" hides it.
2. **Mismatched Reply-To** - replies go to a different address than the From.
3. **Urgency + threat** - "suspended in 24 hours" pressures the victim to act fast.
4. **Credential request** - legitimate IT never asks for your password.
5. **Link text vs destination** - "Click here" hides an untrusted URL; the login name
   is pre-filled in the query string to look personalised.

## Controls (how CampusShield defends against this)
- **SPF, DKIM, DMARC** - email authentication so spoofed sender domains are rejected
  or quarantined by the mail server.
- **User awareness training** - never enter credentials via an emailed link; navigate
  to the service directly.
- **No credentials over links** - combined with account lockout (Task 3) and MFA,
  stolen passwords are far less useful.
- **Link/attachment filtering** at the gateway.

## Interpretation sentence (report)
"The sample shows the classic phishing pattern - spoofed sender, urgency, and a
credential-harvesting link - and the primary technical control is SPF/DKIM/DMARC email
authentication, backed by user training so credentials are never entered via a link."
