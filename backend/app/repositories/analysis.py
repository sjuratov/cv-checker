"""Repository pattern for analysis results."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.models.domain import AnalysisResult


class AnalysisRepository(ABC):
    """Abstract repository for analysis results."""

    @abstractmethod
    async def save(self, analysis: AnalysisResult) -> str:
        """
        Save analysis result.

        Args:
            analysis: AnalysisResult to save

        Returns:
            Document ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """
        Retrieve analysis by ID.

        Args:
            analysis_id: Unique analysis identifier

        Returns:
            AnalysisResult if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_recent(self, limit: int = 10) -> list[AnalysisResult]:
        """
        List recent analyses.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent AnalysisResults
        """
        pass


class InMemoryAnalysisRepository(AnalysisRepository):
    """V1 implementation: No persistence, returns immediately."""

    async def save(self, analysis: AnalysisResult) -> str:
        """
        No-op save - returns ID without persisting.

        In v1, we don't persist data. This implementation allows
        the service layer to work unchanged when we add Cosmos DB in v2+.

        Args:
            analysis: AnalysisResult to save

        Returns:
            Analysis ID
        """
        return analysis.id

    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """
        Always returns None in v1.

        Args:
            analysis_id: Unique analysis identifier

        Returns:
            None (no persistence in v1)
        """
        return None

    async def list_recent(self, limit: int = 10) -> list[AnalysisResult]:
        """
        Returns empty list in v1.

        Args:
            limit: Maximum number of results to return

        Returns:
            Empty list (no persistence in v1)
        """
        return []


# Future Cosmos DB implementation (placeholder for v2+)
class CosmosDBAnalysisRepository(AnalysisRepository):
    """
    V2+ implementation: Persists to Cosmos DB.

    This is a placeholder for future implementation.
    See ADR-004 for Cosmos DB design details.
    """

    def __init__(self, cosmos_client: Any, database_name: str, container_name: str):
        """
        Initialize Cosmos DB repository.

        Args:
            cosmos_client: Azure Cosmos DB client
            database_name: Database name
            container_name: Container name
        """
        raise NotImplementedError("Cosmos DB support will be added in v2+")

    async def save(self, analysis: AnalysisResult) -> str:
        """Save to Cosmos DB with partition key."""
        raise NotImplementedError("Cosmos DB support will be added in v2+")

    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve from Cosmos DB."""
        raise NotImplementedError("Cosmos DB support will be added in v2+")

    async def list_recent(self, limit: int = 10) -> list[AnalysisResult]:
        """Query recent analyses."""
        raise NotImplementedError("Cosmos DB support will be added in v2+")
