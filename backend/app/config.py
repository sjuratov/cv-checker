"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(
        ...,
        description="Azure OpenAI endpoint URL",
    )
    azure_openai_deployment: str = Field(
        default="gpt-4-1",
        description="Azure OpenAI deployment name",
    )
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview",
        description="Azure OpenAI API version",
    )
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key (if not using Entra ID authentication)",
    )

    # Azure Authentication (optional - for service principal)
    azure_tenant_id: Optional[str] = Field(
        default=None,
        description="Azure AD tenant ID",
    )
    azure_client_id: Optional[str] = Field(
        default=None,
        description="Azure service principal client ID",
    )
    azure_client_secret: Optional[str] = Field(
        default=None,
        description="Azure service principal client secret",
    )

    # Application Configuration
    app_env: str = Field(
        default="development",
        description="Application environment",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    # Azure Cosmos DB Configuration (Phase 2)
    cosmos_connection_string: Optional[str] = Field(
        default=None,
        description="Azure Cosmos DB connection string (local emulator or Azure)",
    )
    cosmos_database_name: str = Field(
        default="cv-checker-db",
        description="Cosmos DB database name",
    )
    cosmos_container_name: str = Field(
        default="cv-checker-data",
        description="Cosmos DB container name",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() in ("development", "dev")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() in ("production", "prod")

    @property
    def is_cosmos_enabled(self) -> bool:
        """Check if Cosmos DB is configured."""
        return self.cosmos_connection_string is not None

    @property
    def is_local_cosmos(self) -> bool:
        """Check if using local Cosmos DB emulator."""
        if not self.cosmos_connection_string:
            return False
        return "localhost:8081" in self.cosmos_connection_string


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
