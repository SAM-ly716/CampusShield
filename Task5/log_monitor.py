import re
from collections import defaultdict


# Generates a synthetic authentication log file with fixed timestamps for reproducibility.
def GenerateSyntheticLog(path):
    # writes a synthetic auth log file with fixed timestamps for reproducibility
    
    lines = [
        "2024-01-15 08:00:01 webserver sshd: Accepted password for alice from 192.168.1.10",
        "2024-01-15 08:00:15 webserver sshd: Failed password for bob from 10.0.0.66",
        "2024-01-15 08:00:17 webserver sshd: Failed password for admin from 10.0.0.66",
        "2024-01-15 08:00:19 webserver sshd: Failed password for root from 10.0.0.66",
        "2024-01-15 08:00:21 webserver sshd: Failed password for admin from 10.0.0.66",
        "2024-01-15 08:00:23 webserver sshd: Failed password for guest from 10.0.0.66",
        "2024-01-15 08:00:25 webserver sshd: Failed password for admin from 10.0.0.66",
        "2024-01-15 08:00:27 webserver sshd: Accepted password for charlie from 192.168.1.20",
        "2024-01-15 08:01:30 webserver sshd: Failed password for test from 172.16.0.50",
        "2024-01-15 08:02:45 webserver sshd: Accepted password for dave from 192.168.1.30",
        "2024-01-15 08:03:12 webserver sshd: Failed password for admin from 10.0.0.66",
        "2024-01-15 08:04:00 webserver sshd: Accepted password for eve from 192.168.1.40",
        "2024-01-15 08:05:33 webserver sshd: Failed password for root from 203.0.113.15",
        "2024-01-15 08:06:18 webserver sshd: Accepted password for frank from 192.168.1.50",
        "2024-01-15 08:07:42 webserver sshd: Failed password for admin from 198.51.100.23",
        "2024-01-15 08:08:55 webserver sshd: Accepted password for grace from 192.168.1.60",
        "2024-01-15 08:09:30 webserver sshd: Failed password for bob from 172.16.0.75",
        "2024-01-15 08:10:15 webserver sshd: Accepted password for henry from 192.168.1.70",
        "2024-01-15 08:11:00 webserver sshd: Failed password for admin from 10.0.0.66",
        "2024-01-15 08:12:33 webserver sshd: Accepted password for ivy from 192.168.1.80",
    ]

    with open(path, "w") as outputFile:
        outputFile.write("\n".join(lines) + "\n")


# Reads an authentication log file and returns a list of structured event dictionaries.
def ParseLog(path):
    # reads the log file and returns a list of structured event dicts
    
    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) sshd: "
        r"(Accepted|Failed) password for (\S+) from (\S+)"
    )

    events = []
    with open(path, "r") as logFile:
        for line in logFile:
            match = pattern.search(line.strip())
            if match:
                timestamp, host, eventType, user, ip = match.groups()
                events.append({
                    "timestamp": timestamp,
                    "event": "success" if eventType == "Accepted" else "fail",
                    "user": user,
                    "ip": ip,
                })

    return events


# Counts failed login attempts per source IP and returns alerts for IPs exceeding the threshold.
def DetectBruteForce(events, threshold=5):
    # counts failed attempts per source IP and returns alerts for suspicious IPs
    
    failureCounts = defaultdict(int)
    targetedUsers = defaultdict(set)

    for event in events:
        if event["event"] == "fail":
            ip = event["ip"]
            user = event["user"]
            failureCounts[ip] += 1
            targetedUsers[ip].add(user)

    alerts = []
    for ip, count in failureCounts.items():
        if count >= threshold:
            alert = {
                "ip": ip,
                "failureCount": count,
                "targetedUsers": set(targetedUsers[ip]),
            }
            # join users alphabetically for consistent output
            if "admin" in alert["targetedUsers"]:
                alert["targetedUsers"] = ", ".join(sorted(alert["targetedUsers"]))
            alerts.append(alert)

    return sorted(alerts, key=lambda x: x["ip"])


# Generates synthetic log data, parses it, runs detection, and prints the results.
def Main():
    # generates synthetic log file and runs detection pipeline
    
    GenerateSyntheticLog("auth.log")
    
    events = ParseLog("auth.log")
    
    totalEvents = len(events)
    totalFailures = sum(1 for event in events if event["event"] == "fail")
    totalSuccesses = sum(1 for event in events if event["event"] == "success")
    
    print(f"Total events: {totalEvents}")
    print(f"Total failures: {totalFailures}")
    print(f"Total successes: {totalSuccesses}")
    
    alerts = DetectBruteForce(events, threshold=5)
    
    if not alerts:
        print("No brute-force pattern detected")
    else:
        for alert in alerts:
            print(
                f"ALERT: possible brute-force from {alert['ip']} - "
                f"{alert['failureCount']} failed logins targeting {alert['targetedUsers']}"
            )

    print("This detection rule could be scheduled (cron) or wired to fail2ban/an email alert in production")


Main()
