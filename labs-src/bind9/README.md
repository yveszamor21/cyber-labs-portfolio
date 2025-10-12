# BIND9 Lab Source

This directory contains a minimal, reproducible lab environment for a recursive resolver using BIND9 in Docker.

## Quick start
```bash
docker compose up -d
dig @127.0.0.1 A example.com +dnssec
```

## Files
- `docker-compose.yml` – container definition
- `named.conf.options` – key resolver settings (DNSSEC, QNAME minimization, logging)
- `zones/` – sample zone files (for demonstration; not required for recursion)
