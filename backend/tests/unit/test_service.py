"""Unit tests for CV Checker service."""

import pytest

from app.models.domain import AnalysisResult
from app.services.cv_checker import CVCheckerService


class TestCVCheckerService:
    """Test CVCheckerService."""

    @pytest.mark.asyncio
    async def test_analyze_cv_returns_result(
        self, service, sample_cv_markdown, sample_job_description
    ):
        """Test that analyze_cv returns an AnalysisResult."""
        result = await service.analyze_cv(sample_cv_markdown, sample_job_description)

        assert isinstance(result, AnalysisResult)
        assert 0 <= result.overall_score <= 100
        assert result.id
        assert isinstance(result.skill_matches, list)
        assert isinstance(result.strengths, list)
        assert isinstance(result.gaps, list)
        assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_analyze_cv_mock_data(
        self, service, sample_cv_markdown, sample_job_description
    ):
        """Test that mock analysis returns expected data structure."""
        result = await service.analyze_cv(sample_cv_markdown, sample_job_description)

        # Verify mock data structure
        assert result.overall_score == 85.5
        assert len(result.skill_matches) > 0
        assert len(result.strengths) > 0
        assert len(result.gaps) > 0
        assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_get_analysis_returns_none(self, service):
        """Test that get_analysis returns None in v1."""
        result = await service.get_analysis("any-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_recent_analyses_returns_empty(self, service):
        """Test that list_recent_analyses returns empty list in v1."""
        results = await service.list_recent_analyses()
        assert results == []
