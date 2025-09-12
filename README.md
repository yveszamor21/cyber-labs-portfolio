# Cyber Labs Portfolio

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-success.svg)

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
- **Security Monitoring** - SIEM setup and log analysis
- **Vulnerability Assessment** - Penetration testing methodologies

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yveszamor21/cyber-labs-portfolio.git
   cd cyber-labs-portfolio
   ```

2. Set up development environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. View documentation locally:
   ```bash
   # GitHub Pages will automatically build and serve the docs/
   # Or run locally with Jekyll
   bundle exec jekyll serve
   ```

## 📚 Documentation

Detailed documentation is available in the [docs/](docs/) directory and published via GitHub Pages. Each lab includes:

- **Objectives** - Learning goals and outcomes
- **Methodology** - Step-by-step procedures
- **Results** - Findings and analysis
- **Conclusions** - Key takeaways and lessons learned

## 🛠️ Tools & Technologies

- **DNS Servers**: BIND9, DNSmasq, Pi-hole
- **Network Analysis**: Wireshark, tcpdump, nmap
- **Security Tools**: Nessus, OpenVAS, Metasploit
- **Documentation**: Jekyll, Markdown, GitHub Pages
- **Version Control**: Git, GitHub

## 📋 Requirements

- Git 2.25+
- Docker (for containerized labs)
- Ruby 2.7+ (for Jekyll documentation)
- Python 3.8+ (for custom scripts)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](.github/CONTRIBUTING.md) and submit pull requests for:

- New lab exercises
- Documentation improvements
- Bug fixes and enhancements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Live Documentation](https://yveszamor21.github.io/cyber-labs-portfolio/)
- [Project Issues](https://github.com/yveszamor21/cyber-labs-portfolio/issues)
- [Wiki](https://github.com/yveszamor21/cyber-labs-portfolio/wiki)

## 📞 Contact

For questions or collaboration opportunities, please visit the [Contact](docs/contact.md) page.

---

**⭐ If you find this repository helpful, please consider giving it a star!**
