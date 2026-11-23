#!/bin/bash
# CampusShield host firewall (iptables) - run with sudo in the isolated lab VM only.
# ufw is not installed on the base Kali image and the host-only lab VM has no Internet
# to apt-install it, so the host firewall is implemented with iptables (preinstalled).

set -e

echo "=== Step 1: Flush and set default-deny inbound policy ==="
iptables -F
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "=== Step 2: Allow loopback and established/related traffic ==="
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "=== Step 3: Allow only the demo service (CampusShield web app) ==="
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

echo "=== Step 4: Drop previously exposed ports ==="
iptables -A INPUT -p tcp --dport 3306 -j DROP   # MySQL
iptables -A INPUT -p tcp --dport 23  -j DROP    # Telnet

echo "=== Step 5: Show the resulting ruleset ==="
iptables -L INPUT -n -v --line-numbers

echo "=== Step 6: What this software-only test CAN and CANNOT demonstrate ==="
echo "CAN:    per-host inbound filtering - default-deny with only tcp 5000 permitted."
echo "CANNOT: a live blocked connection from this same VM - traffic to 127.0.0.1 or the"
echo "        host-only IP is delivered via loopback and accepted; prove a real block from"
echo "        a SEPARATE host (see Task 2 Nmap from another zone: port 5000 filtered)."
echo "CANNOT: physical switch-port security or VLAN segmentation - needs network hardware."
