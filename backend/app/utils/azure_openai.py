"""Azure OpenAI client setup with Entra ID authentication using Microsoft Agent Framework."""

import logging
import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureOpenAIChatClient

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class AzureOpenAIConfig:
    """Azure OpenAI configuration manager."""

    def __init__(self, settings: Settings):
        """
        Initialize Azure OpenAI configuration.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.endpoint = settings.azure_openai_endpoint
        self.deployment = settings.azure_openai_deployment
        self.api_version = settings.azure_openai_api_version

        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")

        logger.info(
            f"Azure OpenAI configured: endpoint={self.endpoint}, "
            f"deployment={self.deployment}, api_version={self.api_version}"
        )

    def create_client(self) -> AzureOpenAIChatClient:
        """
        Create Azure OpenAI chat client using Microsoft Agent Framework with Entra ID auth.

        Uses DefaultAzureCredential which tries authentication methods in order:
        1. Environment variables (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
        2. Managed Identity (for Azure-hosted apps)
        3. Azure CLI (az login)
        4. Visual Studio Code Azure extension

        Returns:
            AzureOpenAIChatClient from Microsoft Agent Framework
        """
        logger.info("Creating Microsoft Agent Framework Azure OpenAI client with DefaultAzureCredential")

        # Create credential for Entra ID authentication
        credential = DefaultAzureCredential()

        # Create Microsoft Agent Framework Azure OpenAI chat client
        client = AzureOpenAIChatClient(
            credential=credential,
            endpoint=self.endpoint,
            deployment_name=self.deployment,
            api_version=self.api_version,
        )

        logger.info("Microsoft Agent Framework Azure OpenAI client created successfully")
        return client


@lru_cache()
def get_openai_config(settings: Settings = None) -> AzureOpenAIConfig:
    """
    Get cached Azure OpenAI configuration instance.

    Args:
        settings: Application settings (optional, uses default if not provided)

    Returns:
        Cached AzureOpenAIConfig instance
    """
    if settings is None:
        settings = get_settings()
    return AzureOpenAIConfig(settings)


@lru_cache()
def get_openai_client(settings: Settings = None) -> AzureOpenAIChatClient:
    """
    Get cached Microsoft Agent Framework Azure OpenAI client instance.

    Args:
        settings: Application settings (optional, uses default if not provided)

    Returns:
        Cached AzureOpenAIChatClient instance from Microsoft Agent Framework
    """
    config = get_openai_config(settings)
    return config.create_client()
