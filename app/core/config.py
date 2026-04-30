from functools import lru_cache
import logging

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "Meridian API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
    mcp_request_timeout: float = 30.0
    openai_api_key: str | None = None
    openai_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_BASE_URL", "OPENAI_API_BASE_URL"),
    )
    openai_model: str = "gpt-4.1-mini"
    openai_agent_max_turns: int = 8
    session_memory_turns: int = 6
    chat_api_url: str = "http://127.0.0.1:8000/api/v1/chat"
    gradio_server_name: str = "127.0.0.1"
    gradio_server_port: int = 7860

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def log_startup(self) -> None:
        logging.basicConfig(level=logging.INFO)
        logger.info("starting %s in %s", self.app_name, self.environment)


@lru_cache
def get_settings() -> Settings:
    return Settings()