"""Unit tests for data models."""

import pytest
from pydantic import ValidationError

from app.models.domain import AnalysisResult, CVDocument, JobDescription, SkillMatch
from app.models.requests import AnalyzeRequest
from app.models.responses import AnalyzeResponse, HealthCheckResponse


class TestSkillMatch:
    """Test SkillMatch model."""

    def test_skill_match_valid(self):
        """Test creating a valid SkillMatch."""
        skill = SkillMatch(
            skill_name="Python",
            required=True,
            candidate_has=True,
            proficiency_level="advanced",
            years_experience=5.0,
            match_score=1.0,
        )
        assert skill.skill_name == "Python"
        assert skill.match_score == 1.0

    def test_skill_match_invalid_score(self):
        """Test that invalid match score raises validation error."""
        with pytest.raises(ValidationError):
            SkillMatch(
                skill_name="Python",
                required=True,
                candidate_has=True,
                match_score=1.5,  # Invalid: > 1.0
            )


class TestAnalysisResult:
    """Test AnalysisResult model."""

    def test_analysis_result_valid(self):
        """Test creating a valid AnalysisResult."""
        result = AnalysisResult(
            overall_score=85.5,
            skill_matches=[],
            experience_match={},
            education_match={},
            strengths=["Strong Python"],
            gaps=["Kubernetes"],
            recommendations=["Get K8s cert"],
        )
        assert result.overall_score == 85.5
        assert result.document_type == "cv_analysis"
        assert result.partition_key == "analysis"
        assert result.id  # Auto-generated UUID

    def test_analysis_result_invalid_score(self):
        """Test that invalid overall score raises validation error."""
        with pytest.raises(ValidationError):
            AnalysisResult(
                overall_score=150.0,  # Invalid: > 100
                skill_matches=[],
                experience_match={},
                education_match={},
            )


class TestAnalyzeRequest:
    """Test AnalyzeRequest model."""

    def test_analyze_request_valid(self, sample_cv_markdown, sample_job_description):
        """Test creating a valid AnalyzeRequest."""
        request = AnalyzeRequest(
            cv_markdown=sample_cv_markdown,
            job_description=sample_job_description,
        )
        assert request.cv_markdown
        assert request.job_description

    def test_analyze_request_too_short(self):
        """Test that too short content raises validation error."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(
                cv_markdown="Too short",
                job_description="Also too short",
            )

    def test_analyze_request_empty(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(
                cv_markdown="   ",  # Only whitespace
                job_description="x" * 100,
            )


class TestAnalyzeResponse:
    """Test AnalyzeResponse model."""

    def test_analyze_response_valid(self):
        """Test creating a valid AnalyzeResponse."""
        response = AnalyzeResponse(
            analysis_id="test-id",
            overall_score=85.5,
            skill_matches=[],
            experience_match={},
            education_match={},
            strengths=["Strong Python"],
            gaps=["Kubernetes"],
            recommendations=["Get K8s cert"],
        )
        assert response.overall_score == 85.5
        assert response.analysis_id == "test-id"


class TestHealthCheckResponse:
    """Test HealthCheckResponse model."""

    def test_health_check_response(self):
        """Test creating a valid HealthCheckResponse."""
        response = HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            service="cv-checker-api",
        )
        assert response.status == "healthy"
        assert response.version == "1.0.0"
