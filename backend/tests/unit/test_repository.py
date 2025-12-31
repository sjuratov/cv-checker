"""Unit tests for repository implementations."""

import pytest

from app.models.domain import AnalysisResult, SkillMatch
from app.repositories.analysis import InMemoryAnalysisRepository


class TestInMemoryAnalysisRepository:
    """Test InMemoryAnalysisRepository."""

    @pytest.mark.asyncio
    async def test_save_returns_id(self, repository):
        """Test that save returns the analysis ID."""
        result = AnalysisResult(
            overall_score=85.5,
            skill_matches=[],
            experience_match={},
            education_match={},
        )

        analysis_id = await repository.save(result)
        assert analysis_id == result.id

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none(self, repository):
        """Test that get_by_id always returns None in v1."""
        result = await repository.get_by_id("any-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_recent_returns_empty(self, repository):
        """Test that list_recent returns empty list in v1."""
        results = await repository.list_recent()
        assert results == []
        assert isinstance(results, list)
