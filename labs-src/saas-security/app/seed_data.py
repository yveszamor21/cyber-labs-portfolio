"""Seed the database with demo users, roles, and documents."""
from __future__ import annotations

from sqlalchemy.orm import Session

from .main import Base, SecureDocument, SessionLocal, User, engine, get_password_hash


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    session: Session = SessionLocal()
    try:
        if session.query(User).count() == 0:
            admin = User(
                username="alice",
                hashed_password=get_password_hash("alicepass"),
                role="admin",
                department="security",
                subscription_tier="enterprise",
            )
            manager = User(
                username="bob",
                hashed_password=get_password_hash("bobpass"),
                role="manager",
                department="engineering",
                subscription_tier="pro",
            )
            viewer = User(
                username="charlie",
                hashed_password=get_password_hash("charliepass"),
                role="viewer",
                department="engineering",
                subscription_tier="free",
            )
            session.add_all([admin, manager, viewer])

        if session.query(SecureDocument).count() == 0:
            docs = [
                SecureDocument(
                    title="Engineering Runbook",
                    body="Operational guidelines for deployments.",
                    classification="internal",
                    owner_department="engineering",
                    subscription_required="pro",
                ),
                SecureDocument(
                    title="Product Roadmap",
                    body="Quarterly objectives and strategic planning.",
                    classification="restricted",
                    owner_department="security",
                    subscription_required="enterprise",
                ),
                SecureDocument(
                    title="Public Status Page",
                    body="System status available to all tiers.",
                    classification="public",
                    owner_department="engineering",
                    subscription_required="free",
                ),
            ]
            session.add_all(docs)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed()
