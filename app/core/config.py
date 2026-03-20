from urllib.parse import urlparse, parse_qs
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@taskflow.com"

    @property
    def database_url_no_query(self) -> str:
        """Get database URL without query parameters (for asyncpg)."""
        parsed = urlparse(self.database_url)
        # Reconstruct URL without query params
        base_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}{parsed.path}"
        return base_url

    @property
    def db_ssl_required(self) -> bool:
        """Check if SSL is required based on sslmode query param."""
        parsed = urlparse(self.database_url)
        query_params = parse_qs(parsed.query)
        sslmode = query_params.get('sslmode', [''])[0]
        return sslmode in ('require', 'verify-full', 'verify-ca')


settings = Settings()
