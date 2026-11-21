#!/bin/bash
# =============================================================================
# campusshield-harden.sh - Hardening script for CampusShield lab VMs only.
# Run with sudo in your isolated Kali/Linux VM. Not for production systems.
# Idempotent-ish: safe to run multiple times without destructive side effects.
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Section 1: Create campus group and users
#   csadmin / csregistrar are AUTHORISED (members of the campus group).
#   csstudent is the UNAUTHORISED account - it must NOT be in the campus group,
#   or it would inherit group-read on the 640 data file and the test would not
#   actually demonstrate a denial.
# -----------------------------------------------------------------------------
echo "=== SECTION 1: Creating campus group and users ==="

groupadd campus 2>/dev/null || true

useradd --gid campus --shell /usr/sbin/nologin csadmin 2>/dev/null || true
useradd --gid campus --shell /bin/bash csregistrar 2>/dev/null || true

# csstudent: own primary group, NOT campus
useradd --user-group --shell /usr/sbin/nologin csstudent 2>/dev/null || true
# repair an existing csstudent that an earlier run may have placed in campus
getent group csstudent >/dev/null 2>&1 || groupadd csstudent
usermod -g csstudent csstudent 2>/dev/null || true
gpasswd -d csstudent campus 2>/dev/null || true

# -----------------------------------------------------------------------------
# Section 2: Create app directory structure with least-privilege permissions
# -----------------------------------------------------------------------------
echo "=== SECTION 2: Creating application directories and files ==="

mkdir -p /opt/campushield/data

chown csadmin:campus /opt/campushield
chmod 750 /opt/campushield

# seed synthetic data so an authorised read is visible
printf 'studentId,name,course\n1,Alice Johnson,CS101\n2,Bob Smith,MATH201\n' > /opt/campushield/data/students.db
chown csadmin:campus /opt/campushield/data/students.db
chmod 640 /opt/campushield/data/students.db

ls -l /opt/campushield/data/students.db

# -----------------------------------------------------------------------------
# Section 3: Access control demonstration tests
# -----------------------------------------------------------------------------
echo "=== SECTION 3: Permission access test ==="

echo "--- Testing csstudent (unauthorised - should FAIL) ---"
su -s /bin/bash csstudent -c 'cat /opt/campushield/data/students.db' 2>&1 || true

echo "--- Testing csadmin (authorised - should SUCCEED) ---"
su -s /bin/bash csadmin -c 'cat /opt/campushield/data/students.db' && echo "SUCCESS: Admin can read file."

# -----------------------------------------------------------------------------
# Section 4: Hardening recommendations to implement manually
# -----------------------------------------------------------------------------
echo "=== SECTION 4: Additional hardening recommendations ==="
echo "[RECOMMENDATION] Disable root SSH login in /etc/ssh/sshd_config: PermitRootLogin no"
echo "[RECOMMENDATION] Enforce account lockout with faillock/PAM after repeated failures"
echo "[RECOMMENDATION] Remove unused packages/services: apt autoremove --purge"
echo "[RECOMMENDATION] Enable automatic security updates (unattended-upgrades)"
echo "[RECOMMENDATION] Set a login banner in /etc/motd: Authorized Access Only"
echo "=== Hardening script complete. Review recommendations above. ==="
