# Secure SaaS Lab (FastAPI + PostgreSQL + Redis + Nginx)

This lab demonstrates how to assemble core SaaS security controls in a Python stack. It includes:

- OAuth2 password flow with JWT access tokens.
- Role-based and attribute-based access control (RBAC + ABAC).
- Input validation and parametrized database access.
- Redis-backed rate limiting and Nginx API gateway throttling.
- Audit logging for authentication and data access events.
- Secure-by-default headers and TLS termination in Nginx.
- Docker Compose deployment for an isolated local environment.

## Prerequisites

- Docker + Docker Compose plugin.
- `openssl` or [`mkcert`](https://github.com/FiloSottile/mkcert) to generate local TLS certificates.

## Quick start

1. **Create TLS certificates for Nginx**

   ```bash
   cd labs-src/saas-security
   mkdir -p nginx/certs
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/certs/localhost.key \
     -out nginx/certs/localhost.crt \
     -subj "/CN=localhost"
   ```

2. **Provision environment variables**

   ```bash
   cp .env.example .env
   ```

   Update `.env` with a strong `JWT_SECRET_KEY`, a Redis password, and an optional `JWT_ISSUER` to align tokens with your organization. Set `TRUSTED_PROXIES` to the IPs or CIDR ranges of your load balancer so `X-Forwarded-For` is only honored from known gateways.

3. **Launch the stack**

   ```bash
   docker compose up --build
   ```

   Services:

   - FastAPI app (internal) on `app:8000`.
   - PostgreSQL on `db:5432`.
   - Redis on `redis:6379`.
   - Nginx API gateway exposed on `https://localhost:8443`.

4. **Seed demo data**

   In a new terminal, run:

   ```bash
   docker compose exec app python -m app.seed_data
   ```

   Demo accounts:

   | User     | Role    | Password   | Department  | Tier       |
   |----------|---------|------------|-------------|------------|
   | alice    | admin   | alicepass  | security    | enterprise |
   | bob      | manager | bobpass    | engineering | pro        |
   | charlie  | viewer  | charliepass| engineering | free       |

## Exercising the controls

### 1. Authentication & token misuse detection

```bash
http --verify=nginx/certs/localhost.crt --form POST https://localhost:8443/auth/token \
  username=alice password=alicepass
```

- Replay the JWT with a modified signature to trigger a `401` and observe the audit log capture (`failed_login`).
- Call `POST /auth/logout` to add the token's JTI to the Redis blocklist; any replay attempt after logout is rejected during JWT validation.

### 2. RBAC and ABAC enforcement

- Use Bob's token to call `GET /documents` and observe that only engineering documents with tiers `free` or `pro` are returned.
- Attempt to create a document with Charlie's token and observe a `403` because viewers lack the RBAC role.

### 3. Input validation & SQL injection countermeasure

```bash
http POST https://localhost:8443/simulate/sql-injection \
  Authorization:"Bearer <token>" \
  user_input="'; DROP TABLE users; --" --verify=nginx/certs/localhost.crt
```

The API safely echoes the payload thanks to parametrized SQL and Pydantic validation. Attempted attacks are recorded in the `audit_logs` table.

### 4. Rate limiting

- Rapidly call `/auth/token` more than 5 times per minute from the same client IP to receive a `429` and a `Retry-After` header from the Redis-backed limiter (`rate_limit:login:{ip}`).
- `/auth/register` is capped at 3 requests per hour per IP and `/auth/password-reset` is capped at 2 requests per hour per IP to deter account creation or recovery abuse.
- Rapidly call `/documents` more than 20 times per minute to receive a `429` from the application.
- Exceed ~30 requests per minute via Nginx to hit the gateway throttling before traffic reaches FastAPI.

### 5. Audit log review

```bash
docker compose exec db psql -U saas_app -d saas -c 'SELECT action, details, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 10;'
```

### 6. Secure deployment patterns

- Inspect `Dockerfile` for minimal base image and pinned dependencies.
- Review `nginx/default.conf` for TLS-only exposure, security headers, and upstream isolation.

## Simulated attack scenarios

| Attack vector        | Observation                                                                 | Defensive countermeasure                                                 |
|----------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Credential stuffing  | Multiple `POST /auth/token` failures produce audit log entries.             | Rate limiting + audit alerting.                                          |
| Token tampering      | Altered JWT signature triggers `401` during `whoami`.                       | `JWTError` handling + revoked token detection pattern.                   |
| SQL injection        | Malicious payload logged yet neutralized by parametrized query.             | Strict validation + `text()` with bound parameters.                      |
| Privilege escalation | Viewer attempts to create document returns `403` and logs event.            | `AccessControl.require_role` and ABAC filters.                           |
| Denial of service    | Burst traffic at gateway or app hits `429` from Nginx/Redis limiters.       | Dual-layer rate limiting.                                               |

## Tear down

```bash
docker compose down -v
```

Destroying the stack removes volumes to prevent sensitive data lingering between labs.
