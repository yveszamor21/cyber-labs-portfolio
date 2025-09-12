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
