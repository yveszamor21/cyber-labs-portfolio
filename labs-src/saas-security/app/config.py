"""Application configuration leveraging environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized settings make it easy to audit and override defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "Secure SaaS Lab"
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "saas"
    postgres_user: str = "saas_app"
    postgres_password: str
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str
    jwt_secret_key: str
    jwt_issuer: str = "secure-saas-lab"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    audit_log_retention_days: int = 30


settings = Settings()
