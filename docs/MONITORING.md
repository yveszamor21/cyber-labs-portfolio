# Security Monitoring & Alerting

This lab emphasizes operational visibility for authentication activity. Use these guidelines to instrument alerting, detect anomalies, and funnel data into your SIEM.

## Alerting Rules

- **Credential Brute Force (IP scoped):** Trigger an alert when **5 or more failed login attempts from the same IP occur within 5 minutes**. Include the source IP, usernames targeted, and request paths for triage.
- **Failed Login Spikes (global):** Detect a **cluster of failed logins across all IPs** that exceeds your normal baseline (for example, a 5× increase over the last hour) to surface distributed guessing attacks.
- **Geographic Anomalies:** Flag authentications originating from **new or distant geographies** compared to the user's historical profile. Combine with device fingerprint or ASN changes for higher fidelity.

## Detection Patterns

- Correlate repeated `failed_login` audit events with identical IPs and rapidly changing usernames.
- Look for single accounts experiencing bursts of failures from diverse IP addresses (credential stuffing indicator).
- Surface logins from improbable travel scenarios (e.g., two continents within one hour) using geo-IP enrichment.

## SIEM Integration

- **Splunk:** Index the `audit_logs` table exports (or stream via forwarder) to an index like `auth_events`. Build saved searches implementing the rules above and configure alerts with adaptive response actions (e.g., block offending IPs via SOAR playbooks).
- **ELK / OpenSearch:** Ingest audit events via Filebeat or Logstash into an index such as `saas-audit-*`. Use Kibana dashboards for visualizing failed login trends, geo anomalies, and per-user activity heatmaps.
- Normalize fields to ECS-like names (e.g., `client.ip`, `event.action`, `user.name`, `event.outcome`) to simplify cross-tool detections and correlation.
