from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = "postgresql://zenith:zenith@127.0.0.1:5432/zenith_privacy"
    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret: str = "change-me-in-production-use-long-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_exp_hours: int = 168
    encryption_key: str = ""  # Fernet key
    frontend_origin: str = "http://localhost:3000"
    gmail_max_messages: int = 300
    cors_origins: str = ""  # comma-separated

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip():
            return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return [self.frontend_origin.rstrip("/")]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    print("🔥 DATABASE_URL USED:", s.database_url)  # 👈 DEBUG LINE
    return s