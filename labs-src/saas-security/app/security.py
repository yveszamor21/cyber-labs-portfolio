"""Authorization helpers and JWT payload model."""
from __future__ import annotations

from typing import Optional, Set

from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Minimal JWT claims for the demo."""

    sub: str = Field(..., description="Subject = user id")
    role: str = Field(..., description="Primary RBAC role")
    exp: int
    jti: str = Field(..., description="JWT ID for replay protection")
    iss: str = Field(..., description="Issuer for trust validation")
    iat: int = Field(..., description="Issued-at timestamp")


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
