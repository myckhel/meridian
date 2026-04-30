from functools import lru_cache
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "Meridian API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def log_startup(self) -> None:
        logging.basicConfig(level=logging.INFO)
        logger.info("starting %s in %s", self.app_name, self.environment)


@lru_cache
def get_settings() -> Settings:
    return Settings()