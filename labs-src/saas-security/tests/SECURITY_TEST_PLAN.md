# Security Test Recommendations for JWT and Access Controls

The current service lacks automated coverage beyond runtime compilation checks. The following unit and integration tests target token misuse, role escalation, and replay behaviors observed in the FastAPI stack defined in `app/main.py` and supporting helpers in `app/security.py`.

## JWT Misuse and Tampering
- **Tampered signature**: Issue a valid token via `/auth/token`, flip a character in the signature, and call a protected route (e.g., `GET /whoami`). Expect `401` from `get_current_user` JWT decode failure.
- **Wrong algorithm header**: Forge a token with `alg="none"` or a mismatched algorithm vs. `settings.jwt_algorithm` and assert `401` due to `JWTError` during decode.
- **Expired token**: Generate a token with `exp` in the past and verify `401` when hitting `GET /documents` because `jwt.decode` enforces the claim.
- **Subject mismatch**: Create a token with a nonexistent `sub` and confirm `401` from `get_current_user` when the user lookup returns `None`.
- **Inactive user**: Mark a user `is_active=False`, reuse their previously issued token, and ensure `get_current_user` rejects it with `401`.

## Role Escalation and RBAC/ABAC Checks
- **Create document as viewer**: Use a `viewer` token against `POST /documents` and expect `403` from `AccessControl.require_role`.
- **Manager outside department**: A `manager` from department A attempts to create a doc for department B and is blocked (either by request validation or ABAC expectations) with `403`.
- **List documents classification filter**: Seed documents with mixed classifications/tier/department. Confirm `viewer` tokens only receive `public` docs matching their department and tier, while `manager` sees departmental docs regardless of classification and `admin` sees all.
- **SQL injection simulator restricted to admin**: Invoke `POST /simulate/sql-injection` using `viewer` and `manager` tokens and assert `403`.
- **Tier downgrades**: Ensure `AccessControl.allowed_tiers` prevents `viewer` or `manager` with `free` tier from seeing `pro`/`enterprise` docs in `GET /documents` responses.

## Replay and Session Handling
- **Token reuse after logout**: Call `/auth/logout` then reuse the same token on `GET /whoami`; document the current behavior (still accepted) and track as a gap or future mitigation requirement.
- **Multiple rapid replays**: Send the same valid token to protected endpoints in quick succession while hitting rate limiter (`Depends(rate_limiter)`) to ensure throttling is enforced and does not skip authentication paths.
- **Expired token replay**: Attempt to reuse an expired token and verify consistent `401` responses with audit logs reflecting failed access attempts when `record_audit_event` is invoked in downstream routes.

## Audit Log Assertions
- For authentication events (`/auth/token`, `/auth/logout`) and protected routes, validate that `AuditLog` rows contain `ip_address`, `action`, `details`, and `user_id` where applicable. Include checks for retention pruning behavior triggered inside `record_audit_event`.

## Test Harness Suggestions
- Use **pytest** with **httpx.AsyncClient** and the FastAPI `TestClient` pattern to spin up the app, using a temporary PostgreSQL database or SQLite (if compatible) and ephemeral Redis for `RateLimiter` initialization.
- Provide fixtures for creating users with each role/tier combination, issuing tokens via `/auth/token`, and injecting request IPs via the test client to assert audit metadata.
- Mock `settings.jwt_secret_key` during token forgery tests to prevent cross-contamination with production secrets and keep fixtures deterministic.

These tests will exercise the key enforcement points in `get_current_user`, `AccessControl.require_role`, and `record_audit_event` to catch regressions in JWT validation, RBAC/ABAC logic, and audit coverage.
