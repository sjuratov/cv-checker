"""Integration tests for API endpoints."""

import pytest


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, test_client):
        """Test GET /api/v1/health returns healthy status."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["service"] == "cv-checker-api"


class TestAnalyzeEndpoint:
    """Test CV analysis endpoint."""

    def test_analyze_success(
        self, test_client, sample_cv_markdown, sample_job_description
    ):
        """Test POST /api/v1/analyze with valid data."""
        response = test_client.post(
            "/api/v1/analyze",
            json={
                "cv_markdown": sample_cv_markdown,
                "job_description": sample_job_description,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "analysis_id" in data
        assert "overall_score" in data
        assert "skill_matches" in data
        assert "experience_match" in data
        assert "education_match" in data
        assert "strengths" in data
        assert "gaps" in data
        assert "recommendations" in data

        # Verify data types and ranges
        assert isinstance(data["overall_score"], (int, float))
        assert 0 <= data["overall_score"] <= 100
        assert isinstance(data["skill_matches"], list)
        assert isinstance(data["strengths"], list)
        assert isinstance(data["gaps"], list)
        assert isinstance(data["recommendations"], list)

    def test_analyze_empty_cv(self, test_client, sample_job_description):
        """Test POST /api/v1/analyze with empty CV."""
        response = test_client.post(
            "/api/v1/analyze",
            json={
                "cv_markdown": "",
                "job_description": sample_job_description,
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"

    def test_analyze_too_short_cv(self, test_client):
        """Test POST /api/v1/analyze with too short CV."""
        response = test_client.post(
            "/api/v1/analyze",
            json={
                "cv_markdown": "Too short",
                "job_description": "x" * 100,
            },
        )

        assert response.status_code == 422

    def test_analyze_missing_job_description(self, test_client, sample_cv_markdown):
        """Test POST /api/v1/analyze without job description."""
        response = test_client.post(
            "/api/v1/analyze",
            json={
                "cv_markdown": sample_cv_markdown,
            },
        )

        assert response.status_code == 422


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root(self, test_client):
        """Test GET / returns API info."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


class TestOpenAPISpec:
    """Test OpenAPI specification generation."""

    def test_openapi_json(self, test_client):
        """Test OpenAPI JSON is generated."""
        response = test_client.get("/api/v1/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_ui(self, test_client):
        """Test Swagger UI is accessible."""
        response = test_client.get("/api/v1/docs")
        assert response.status_code == 200

    def test_redoc_ui(self, test_client):
        """Test ReDoc UI is accessible."""
        response = test_client.get("/api/v1/redoc")
        assert response.status_code == 200
