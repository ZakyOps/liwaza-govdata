from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Liwaza GovData Assistant API"
    app_version: str = "0.1.0"
    environment: str = "development"
    datafair_base_url: str = "https://data.gouv.ci/data-fair/api/v1"
    request_timeout_seconds: float = 12.0
    api_key: str | None = Field(default=None, alias="API_KEY")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
