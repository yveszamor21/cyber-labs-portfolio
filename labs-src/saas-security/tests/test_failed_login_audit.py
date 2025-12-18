import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure environment variables required by the app are populated before import
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_USER", "tester")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "dummy")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ISSUER", "test-issuer")

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app import main  # noqa: E402  pylint: disable=wrong-import-position


class DummyRateLimiter:
    async def initialize(self):
        return None

    async def close(self):
        return None

    async def __call__(self, request):  # pragma: no cover - interface compatibility
        return None


class DummyTokenBlocklist:
    async def initialize(self):
        return None

    async def close(self):
        return None

    async def is_blocked(self, jti: str) -> bool:
        return False

    async def block_until_expiry(self, jti: str, exp_timestamp: int) -> None:
        return None


@pytest.fixture()
def test_client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    # Swap out database bindings
    main.engine = engine
    main.SessionLocal = TestingSessionLocal
    main.Base.metadata.create_all(bind=engine)

    # Override dependencies to avoid external Redis requirements
    dummy_rate_limiter = DummyRateLimiter()
    dummy_blocklist = DummyTokenBlocklist()
    original_rate_limiter = main.rate_limiter
    main.rate_limiter = dummy_rate_limiter
    main.token_blocklist = dummy_blocklist
    main.app.dependency_overrides[original_rate_limiter] = dummy_rate_limiter

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    main.app.dependency_overrides[main.get_db] = override_get_db

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides.clear()


@pytest.fixture()
def db_session(test_client):
    with main.SessionLocal() as session:
        yield session


def create_user(db_session):
    user = main.User(
        username="alice",
        hashed_password=main.get_password_hash("correct-horse-battery-staple"),
        role="viewer",
        department="engineering",
        subscription_tier="pro",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_failed_login_persists_audit_logs(test_client, db_session):
    create_user(db_session)

    response = test_client.post(
        "/auth/token",
        data={"username": "alice", "password": "wrong-password"},
        headers={"x-forwarded-for": "203.0.113.5"},
    )

    assert response.status_code == 401

    audit_entries = db_session.query(main.AuditLog).all()
    assert len(audit_entries) == 1
    entry = audit_entries[0]
    assert entry.action == "failed_login"
    assert entry.ip_address == "203.0.113.5"
    assert "username=alice bad_credentials" in entry.details


def test_multiple_failed_logins_are_recorded(test_client, db_session):
    create_user(db_session)

    for _ in range(3):
        test_client.post(
            "/auth/token",
            data={"username": "alice", "password": "wrong-password"},
            headers={"x-forwarded-for": "198.51.100.7"},
        )

    entries = db_session.query(main.AuditLog).all()
    assert len(entries) == 3
    assert all(entry.action == "failed_login" for entry in entries)
    assert all(entry.ip_address == "198.51.100.7" for entry in entries)
