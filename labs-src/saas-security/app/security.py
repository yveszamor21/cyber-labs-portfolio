"""Authorization helpers, JWT payload model, and trusted IP parsing."""
from __future__ import annotations

import ipaddress
from typing import Optional, Set

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

from .config import settings

TRUSTED_PROXIES = []
for proxy in settings.trusted_proxies:
    try:
        TRUSTED_PROXIES.append(ipaddress.ip_network(proxy, strict=False))
    except ValueError:
        TRUSTED_PROXIES.append(proxy)


class TokenPayload(BaseModel):
    """Minimal JWT claims for the demo."""

    sub: str = Field(..., description="Subject = user id")
    role: str = Field(..., description="Primary RBAC role")
    exp: int
    jti: str = Field(..., description="JWT ID for replay protection")
    iss: str = Field(..., description="Issuer for trust validation")
    iat: int = Field(..., description="Issued-at timestamp")


def _is_trusted_proxy(client_host: str | None) -> bool:
    if not client_host:
        return False
    try:
        client_ip = ipaddress.ip_address(client_host)
    except ValueError:
        client_ip = None

    for proxy in TRUSTED_PROXIES:
        if isinstance(proxy, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
            if client_ip and client_ip in proxy:
                return True
        elif proxy == client_host:
            return True
    return False


def _is_public_ip(candidate: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(candidate)
    except ValueError:
        return False
    return not (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
        or ip_obj.is_multicast
    )


def extract_client_ip(request: Request) -> str:
    """Safely determine caller IP honoring trusted proxy chain."""

    remote_host = request.client.host if request.client else None
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for and _is_trusted_proxy(remote_host):
        for part in forwarded_for.split(","):
            candidate = part.strip()
            if _is_public_ip(candidate):
                return candidate

    return remote_host or "unknown"


class AccessControl:
    """Combined RBAC + ABAC helper functions."""

    tier_hierarchy = {
        "free": {"free"},
        "pro": {"free", "pro"},
        "enterprise": {"free", "pro", "enterprise"},
    }

    def require_role(self, role: str, *, allowed_roles: Set[str]) -> None:
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges",
            )

    def is_admin(self, role: str) -> bool:
        return role == "admin"

    def allowed_tiers(self, user_tier: str) -> Set[str]:
        return self.tier_hierarchy.get(user_tier, {"free"})

    def can_access_document(
        self,
        *,
        role: str,
        department: str,
        subscription_tier: str,
        document_department: str,
        document_tier: str,
        document_classification: str,
    ) -> bool:
        """ABAC rules combining role, department, and subscription tier."""

        if self.is_admin(role):
            return True
        if role == "manager" and department == document_department:
            return document_tier in self.allowed_tiers(subscription_tier)
        if role == "viewer":
            return (
                document_department == department
                and document_classification == "public"
                and document_tier in self.allowed_tiers(subscription_tier)
            )
        return False
