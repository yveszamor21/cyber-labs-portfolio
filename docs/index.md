---
layout: default
title: Cyber Labs Portfolio Documentation
description: Comprehensive cybersecurity laboratory exercises and research documentation
permalink: /
---

# Cyber Labs Portfolio Documentation

## Welcome to the Cyber Labs Portfolio

This repository contains a comprehensive collection of cybersecurity laboratory exercises, research projects, and technical documentation. The portfolio demonstrates practical experience with network security, DNS configurations, traffic analysis, and security monitoring tools.

## 📖 Navigation

### Laboratory Exercises
- [DNS Security Labs](labs/dns-security/)
- [Network Traffic Analysis](labs/network-analysis/)
- [Security Monitoring](labs/security-monitoring/)
- [Vulnerability Assessment](labs/vulnerability-assessment/)

### Documentation
- [About This Portfolio](about.html)
- [Contact Information](contact.html)
- [Lab Setup Guide](setup-guide.html)

## 🔧 Technologies Covered

### DNS Security
- **BIND9** - Advanced DNS server configuration and security hardening
- **DNSmasq** - Lightweight DNS/DHCP services
- **Pi-hole** - Network-wide ad blocking and DNS filtering

### Network Analysis Tools
- **Wireshark** - Network protocol analyzer and packet capture
- **tcpdump** - Command-line packet analyzer
- **nmap** - Network discovery and security auditing

### Security Monitoring
- **SIEM Solutions** - Security Information and Event Management
- **Log Analysis** - Centralized logging and correlation
- **Threat Detection** - Real-time security monitoring

## 🚀 Getting Started

### Prerequisites
- Git 2.25+
- Docker (for containerized labs)
- Ruby 2.7+ (for local Jekyll development)
- Python 3.8+ (for custom scripts)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yveszamor21/cyber-labs-portfolio.git
   cd cyber-labs-portfolio
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Run locally:**
   ```bash
   bundle install
   bundle exec jekyll serve
   ```

## 📚 Lab Structure

Each laboratory exercise follows a consistent structure:

- **Objectives** - Clear learning goals and expected outcomes
- **Prerequisites** - Required knowledge and setup requirements
- **Methodology** - Step-by-step procedures and commands
- **Results** - Detailed findings and analysis
- **Conclusions** - Key takeaways and lessons learned
- **References** - Additional resources and documentation

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](../CONTRIBUTING.md) for details on:

- Submitting new lab exercises
- Improving documentation
- Reporting issues and bugs
- Suggesting enhancements

## 📄 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/yveszamor21/cyber-labs-portfolio)
- [Issues Tracker](https://github.com/yveszamor21/cyber-labs-portfolio/issues)
- [Wiki](https://github.com/yveszamor21/cyber-labs-portfolio/wiki)
- [Live Documentation](https://yveszamor21.github.io/cyber-labs-portfolio/)

---

**Last Updated:** {{ site.time | date: "%B %d, %Y" }}
**Version:** 1.0.0
