# Cyber Labs Portfolio

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Build Status](https://img.shields.io/badge/build-passing-success.svg)

## 🎯 Review Me Fast

**Who I Am:** Cybersecurity professional with hands-on expertise in DNS security, network traffic analysis, and security monitoring infrastructure.

**Target Roles:** SOC Analyst | Security Engineer | Network Security Analyst

**Top 3 Labs:**
1. [DNS Security Analysis (BIND9)](https://yveszamor21.github.io/cyber-labs-portfolio/labs/dns-bind9.html) - DNS server hardening and security monitoring
2. [Network Traffic Analysis](https://yveszamor21.github.io/cyber-labs-portfolio/) - Wireshark deep packet inspection and threat detection
3. [Security Monitoring with Pi-hole](https://yveszamor21.github.io/cyber-labs-portfolio/) - DNS-based threat blocking and analytics

**Run Locally:** Clone repo → `cd cyber-labs-portfolio` → Open `docs/index.html` in browser

**Live Site:** [https://yveszamor21.github.io/cyber-labs-portfolio/](https://yveszamor21.github.io/cyber-labs-portfolio/)

---

## Overview

This repository contains a comprehensive collection of cybersecurity laboratory exercises, research projects, and technical documentation. The portfolio demonstrates practical experience with network security, DNS configurations, traffic analysis, and security monitoring tools.

## 🏗️ Repository Structure

```
cyber-labs-portfolio/
├── docs/                    # Documentation and lab reports
│   ├── labs/               # Individual lab documentation
│   ├── about.md            # About page
│   ├── contact.md          # Contact information
│   └── index.md            # Main documentation index
├── assets/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── images/            # Screenshots and diagrams
│   └── diagrams/          # Network diagrams and flowcharts
├── labs-src/              # Source code and configurations
│   ├── bind9/             # BIND9 DNS server configurations
│   ├── dnsmasq/           # DNSmasq configurations
│   ├── pihole/            # Pi-hole DNS configurations
│   └── tools/             # Custom scripts and utilities
└── .github/               # GitHub workflows and templates
    ├── workflows/         # CI/CD pipelines
    └── ISSUE_TEMPLATE/    # Issue templates
```

## 🧪 Featured Labs

- **DNS Security Analysis** - BIND9, DNSmasq, and Pi-hole configurations
- **Network Traffic Analysis** - Wireshark and tcpdump investigations
- **Security Monitoring** - Log analysis and threat detection
- **Vulnerability Assessment** - Network scanning and security auditing

## 🚀 Getting Started

### Prerequisites

- Git
- Web browser for viewing documentation
- Linux environment (recommended for running lab configurations)

### Installation

```bash
git clone https://github.com/yveszamor21/cyber-labs-portfolio.git
cd cyber-labs-portfolio
```

### Viewing Documentation

Open `docs/index.html` in your web browser or visit the live site at [https://yveszamor21.github.io/cyber-labs-portfolio/](https://yveszamor21.github.io/cyber-labs-portfolio/)

## 📚 Documentation

Detailed lab reports and documentation are available in the `/docs` directory. Each lab includes:

- Objective and scope
- Architecture diagrams
- Step-by-step configuration
- Command references
- Evidence and findings
- Security recommendations
- Lessons learned

## 🛠️ Technologies Used

- **DNS Servers:** BIND9, DNSmasq, Pi-hole
- **Network Analysis:** Wireshark, tcpdump, tshark
- **Security Tools:** Nmap, OpenVAS, Nikto
- **Documentation:** Markdown, GitHub Pages
- **Version Control:** Git, GitHub

## 🔒 Security Highlights (SaaS Lab)

- **Failed login audit persistence** using isolated transactions to ensure bad credential attempts are captured for forensics.
- **Rate limiting on authentication endpoints** to slow brute force attempts and protect credentials.
- **JWT replay protection** via a Redis-backed token blocklist that revokes tokens on logout or suspicion.
- **Proxy-aware IP logging** that honors `X-Forwarded-For` to preserve accurate client attribution behind gateways.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions or collaboration opportunities, please reach out through the [contact page](https://yveszamor21.github.io/cyber-labs-portfolio/contact.html).

## 🌐 Live Documentation

[View Portfolio Site](https://yveszamor21.github.io/cyber-labs-portfolio/)
