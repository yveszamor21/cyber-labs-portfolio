# DNS Security Lab — BIND9 (Docker)

**Date tested:** October 12, 2025  
**Target roles:** SOC Analyst / Jr. Security Engineer  
**Tools:** BIND 9.18 (docker), `dig`, `drill`, `tcpdump`, Wireshark

## Objectives
1. Stand up a local recursive resolver (BIND9) in Docker.
2. Enable **QNAME minimization** and **DNSSEC validation**.
3. Generate traffic and logs; confirm defenses via **evidence**.
4. Explore cache-poisoning risk surface and show mitigations.

## Architecture

![Homelab DNS Diagram](../assets/diagrams/homelab-dns-arch.drawio.svg)

- Client host runs `dig`/`drill` and sends queries to resolver.
- Resolver: containerized BIND9, with query logging and DNSSEC on.
- Upstream: public resolvers / authoritative servers on the Internet.

## Reproducible Setup

> Requires: Docker Desktop or Docker Engine.

```bash
git clone https://github.com/yveszamor21/cyber-labs-portfolio.git
cd cyber-labs-portfolio/labs-src/bind9
docker compose up -d
```

- The resolver listens on `127.0.0.1:53` (TCP/UDP) and `0.0.0.0:53` (mapped from the container).  
- To make your host use it temporarily:
  - Linux/macOS: `sudo bash -c 'echo nameserver 127.0.0.1 > /etc/resolv.conf'` (remember to restore later), or use `dig @127.0.0.1 ...` per-command.
  - Safer: keep system resolver unchanged and always pass `@127.0.0.1` to tools.

## Configuration Highlights

- **QNAME minimization:** only sends the minimal necessary labels upstream.
- **DNSSEC validation:** validates signed zones (AD flag set on success).
- **Query logging:** to observe lookups and caching behavior.

Key file: `labs-src/bind9/named.conf.options`

```conf
options {
    directory "/var/cache/bind";
    recursion yes;
    allow-recursion { any; };

    // QNAME Minimization
    qname-minimization yes;

    // DNSSEC
    dnssec-validation auto;

    // Logging
    querylog yes;

    listen-on port 53 { any; };
};
```

## Tasks & Evidence

### 1) Baseline lookups and caching
Run:
```bash
dig @127.0.0.1 A example.com +dnssec +multi
dig @127.0.0.1 AAAA example.com +dnssec +multi
dig @127.0.0.1 A www.example.com +dnssec +multi
```
**Evidence to collect:**
- Screenshot of terminal showing **`status: NOERROR`** and **`ad`** (Authenticated Data) flag when DNSSEC validated.
- `;; SERVER: 127.0.0.1#53` confirms queries hit your resolver.
- A second run should be faster (cached). Note **`Query time:`** delta.

### 2) Validate DNSSEC on signed zones
Try a signed TLD/domain, e.g. `.org` or `dnssec-failed.org` (intentionally broken for testing):
```bash
dig @127.0.0.1 A ietf.org +dnssec
dig @127.0.0.1 A dnssec-failed.org +dnssec
```
**Expected:**
- `ietf.org` resolves with `ad` flag.
- `dnssec-failed.org` should **fail validation** (SERVFAIL or no `ad`).

Capture a screenshot and note the behavior differences.

### 3) Observe QNAME minimization behavior
Use `+trace` with a public resolver comparison (do not change your system DNS permanently):
```bash
dig +trace A www.example.com
dig @127.0.0.1 +trace A www.example.com
```
**Observation:** With minimization, upstream queries are minimized to necessary labels.  
(Deep packet capture requires `tcpdump` running on the host interface while resolving.)

### 4) Inspect query logs
Enter the container and view logs:
```bash
docker compose logs -f bind9
# or
docker exec -it bind9 sh -c 'grep -i query /var/log/named/query.log || tail -f /var/log/named/*.log'
```
**Evidence:** Paste a few log lines showing query types, client IP, and whether answers were served from cache or upstream.

> Note: Some images log via stderr/stdout; `docker compose logs bind9` will show query activity when `querylog yes;` is set.

### 5) Cache poisoning surface (theory → practice)
- Classic poisoning relies on predicting TXID/port or racing the legitimate response.
- Modern BIND uses random source ports and strong TXID randomness; **DNSSEC** thwarts forged data even if a race succeeds.
- **Exercise:** Run repeated lookups for a non-existent subdomain to generate NXDOMAIN cache entries and note TTLs:
```bash
for i in $(seq 1 5); do dig @127.0.0.1 A no-such-$i.example.com +dnssec; done
```
**Evidence:** Show NXDOMAIN with SOA in the authority section and the negative cache TTL.

## Hardening Checklist (you did)
- [x] QNAME minimization: `yes`
- [x] DNSSEC validation: `auto`
- [x] Query logging: on (during lab)
- [x] Non-recursive on authoritative servers (N/A in this lab)
- [x] Limit recursion to trusted networks (tighten in production)

## What I’d do in production
- Limit recursion to corp subnets only.
- Forward to internal **validating** resolver pair with health checks.
- Centralize logs to SIEM (Suricata/Splunk) with dashboards for NXDOMAIN spikes and query volume anomalies.
- Enable rate limiting (RRL) to reduce abuse amplification.
- Document resolver version and patch cadence (watch CVEs).

## Clean Up
```bash
docker compose down
```

## Reflection
- **Finding:** DNSSEC provided authenticated data on signed zones and blocked intentionally-bad domains.
- **Impact:** Reduces phishing/poisoning blast radius; improves integrity for downstream systems (proxy, EDR updaters).
- **Next:** Ship Suricata + Splunk lab to alert on suspicious DNS patterns (e.g., DGA, high NXDOMAIN rates).
