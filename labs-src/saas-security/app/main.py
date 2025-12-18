"""Secure SaaS reference implementation with extensive inline guidance."""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

from .config import settings
from .rate_limiter import RateLimiter
from .security import AccessControl, TokenPayload

# ---------------------------------------------------------------------------
# Database bootstrap
# ---------------------------------------------------------------------------
DATABASE_URL = (
    f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


class User(Base):
    """Simple user table demonstrating RBAC and ABAC attributes."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    department = Column(String(50), nullable=False, default="general")
    subscription_tier = Column(String(20), nullable=False, default="free")
    is_active = Column(Boolean, default=True)

    audit_logs = relationship("AuditLog", back_populates="user")


class SecureDocument(Base):
    """Sensitive business data protected via RBAC + ABAC."""

    __tablename__ = "secure_documents"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    body = Column(String(2000), nullable=False)
    classification = Column(String(20), nullable=False)
    owner_department = Column(String(50), nullable=False)
    subscription_required = Column(String(20), nullable=False, default="free")


class AuditLog(Base):
    """Persist audit events for forensic readiness."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(150), nullable=False)
    ip_address = Column(String(45), nullable=False)
    details = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False)

    user = relationship("User", back_populates="audit_logs")


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=True)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenResponse(BaseModel):
    """Shape of the access token response."""

    access_token: str
    token_type: str = "bearer"


class DocumentIn(BaseModel):
    """Validate inbound JSON and limit attack surface area."""

    title: str = Field(..., max_length=150, pattern=r"^[\w\s\-]+$")
    body: str = Field(..., max_length=2000)
    classification: str = Field(..., pattern=r"^(public|internal|restricted)$")
    owner_department: str = Field(..., max_length=50)
    subscription_required: str = Field(..., pattern=r"^(free|pro|enterprise)$")


class DocumentOut(BaseModel):
    id: int
    title: str
    body: str
    classification: str
    owner_department: str
    subscription_required: str

    class Config:
        orm_mode = True


class SQLInjectionPayload(BaseModel):
    """Used to demonstrate input validation + parametrized queries."""

    user_input: str = Field(..., max_length=200)


access_control = AccessControl()
rate_limiter = RateLimiter(redis_host=settings.redis_host, redis_port=settings.redis_port)
app = FastAPI(title=settings.project_name)


# Dependency helper ensures sessions are closed even if exceptions occur.
@contextmanager
def session_scope() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as exc:  # pragma: no cover - demo resilience
        session.rollback()
        raise exc
    finally:
        session.close()


async def get_db():
    with session_scope() as session:
        yield session


# ---------------------------------------------------------------------------
# Authentication & Authorization flows
# ---------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).one_or_none()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(*, data: dict, expires_delta: dt.timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + (expires_delta or dt.timedelta(minutes=settings.jwt_access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Decode JWT token and fetch an active user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload.model_validate(payload)
    except JWTError as exc:  # token misuse / tampering detection
        raise credentials_exception from exc

    user = db.get(User, token_data.sub)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ---------------------------------------------------------------------------
# Audit logging utilities
# ---------------------------------------------------------------------------
def record_audit_event(db: Session, *, user: Optional[User], request: Request, action: str, details: str) -> None:
    """Persist security-relevant events for accountability."""

    ip_address = request.client.host if request.client else "unknown"
    audit_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        ip_address=ip_address,
        details=details,
    )
    db.add(audit_entry)
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=settings.audit_log_retention_days)
    db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.post("/auth/token", response_model=TokenResponse)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    """Issue signed JWT access tokens."""

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        record_audit_event(
            db,
            user=None,
            request=request,
            action="failed_login",
            details=f"username={form_data.username} bad_credentials",
        )
        try:
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to record failed login audit",
            ) from exc
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    record_audit_event(
        db,
        user=user,
        request=request,
        action="login",
        details=f"username={user.username} issued token",
    )
    return TokenResponse(access_token=access_token)


@app.post("/auth/logout")
async def logout(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Record logout events for accountability."""

    record_audit_event(
        db,
        user=current_user,
        request=request,
        action="logout",
        details=f"username={current_user.username} logout",
    )
    return {"detail": "Logged out"}


@app.post("/documents", response_model=DocumentOut)
async def create_document(
    request: Request,
    payload: DocumentIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[None, Depends(rate_limiter)],
):
    """Create a document with RBAC enforcement (admin + manager roles)."""

    access_control.require_role(current_user.role, allowed_roles={"admin", "manager"})
    record_audit_event(db, user=current_user, request=request, action="create_document", details=payload.title)

    document = SecureDocument(**payload.model_dump())
    db.add(document)
    db.flush()
    return document


@app.get("/documents", response_model=list[DocumentOut])
async def list_documents(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[None, Depends(rate_limiter)],
):
    """List documents applying ABAC constraints."""

    record_audit_event(db, user=current_user, request=request, action="list_documents", details="view")

    # Enforce ABAC: restrict results to user's department, tier, and classification unless admin.
    if access_control.is_admin(current_user.role):
        return db.query(SecureDocument).all()

    candidate_docs = db.query(SecureDocument).filter(
        SecureDocument.owner_department == current_user.department,
        SecureDocument.subscription_required.in_(
            access_control.allowed_tiers(current_user.subscription_tier)
        ),
    )

    # Apply fine-grained classification filtering for viewers.
    documents = []
    for doc in candidate_docs:
        if access_control.can_access_document(
            role=current_user.role,
            department=current_user.department,
            subscription_tier=current_user.subscription_tier,
            document_department=doc.owner_department,
            document_tier=doc.subscription_required,
            document_classification=doc.classification,
        ):
            documents.append(doc)
    return documents


@app.post("/simulate/sql-injection")
async def simulate_sql_injection(
    request: Request,
    payload: SQLInjectionPayload,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Demonstrate safe parametrized queries mitigating SQL injection."""

    access_control.require_role(current_user.role, allowed_roles={"admin"})
    record_audit_event(db, user=current_user, request=request, action="simulate_sql_injection", details=payload.user_input)

    # Untrusted input could look like: "'; DROP TABLE users; --"
    # Instead of string concatenation, we use bound parameters that the
    # database treats as data instead of executable SQL.
    result = db.execute(
        text("SELECT :user_input AS sanitized"),
        {"user_input": payload.user_input},
    )
    return {"echo": result.scalar_one()}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Secure-by-default HTTP headers via API gateway defense-in-depth."""

    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


@app.on_event("startup")
async def on_startup() -> None:
    """Create tables + warm up rate limiter."""

    Base.metadata.create_all(bind=engine)
    app.state.rate_limiter = rate_limiter
    await rate_limiter.initialize()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await rate_limiter.close()


# Utility endpoint to showcase token misuse detection.
@app.get("/whoami")
async def whoami(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    record_audit_event(db, user=current_user, request=request, action="whoami", details="self check")
    return {
        "username": current_user.username,
        "role": current_user.role,
        "department": current_user.department,
        "subscription_tier": current_user.subscription_tier,
    }
