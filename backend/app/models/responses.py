"""API response models."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class SkillMatchResponse(BaseModel):
    """Individual skill match in API response."""

    skill_name: str = Field(description="Name of the skill")
    required: bool = Field(description="Whether this skill is required")
    candidate_has: bool = Field(description="Whether candidate has this skill")
    proficiency_level: Optional[str] = Field(
        default=None,
        description="Proficiency level",
    )
    years_experience: Optional[float] = Field(
        default=None,
        description="Years of experience",
    )
    match_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Match score (0.0 to 1.0)",
    )


class AnalyzeResponse(BaseModel):
    """Response model for CV analysis."""

    analysis_id: str = Field(description="Unique analysis identifier")
    overall_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall match score (0-100)",
    )
    skill_matches: list[SkillMatchResponse] = Field(
        description="Detailed skill matching results"
    )
    experience_match: dict[str, Any] = Field(description="Experience level analysis")
    education_match: dict[str, Any] = Field(description="Education requirements analysis")
    strengths: list[str] = Field(description="Candidate strengths for this role")
    gaps: list[str] = Field(description="Identified skill/experience gaps")
    recommendations: list[str] = Field(description="Actionable recommendations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
                "overall_score": 85.5,
                "skill_matches": [
                    {
                        "skill_name": "Python",
                        "required": True,
                        "candidate_has": True,
                        "proficiency_level": "advanced",
                        "years_experience": 5.0,
                        "match_score": 1.0,
                    }
                ],
                "experience_match": {
                    "required_years": 5,
                    "candidate_years": 6,
                    "match": True,
                },
                "education_match": {
                    "required": "Bachelor's in Computer Science",
                    "candidate": "Master's in Computer Science",
                    "match": True,
                },
                "strengths": [
                    "Strong Python expertise with 6 years experience",
                    "Advanced cloud architecture skills",
                    "Excellent leadership experience",
                ],
                "gaps": [
                    "Limited Kubernetes experience",
                    "No mention of GraphQL",
                ],
                "recommendations": [
                    "Consider Kubernetes certification to strengthen DevOps profile",
                    "Add GraphQL projects to portfolio",
                    "Highlight any microservices experience more prominently",
                ],
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error context",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": {
                    "field": "cv_markdown",
                    "issue": "Content too short",
                },
            }
        }
    }


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    service: str = Field(description="Service name")
    azure_openai: Optional[str] = Field(
        default=None,
        description="Azure OpenAI connection status",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "service": "cv-checker-api",
                "azure_openai": "connected",
            }
        }
    }


class JobSubmissionResponse(BaseModel):
    """Response model for job submission."""

    job_id: str = Field(description="Unique job identifier")
    content: str = Field(description="Job description content")
    source_type: Literal["manual", "linkedin_url"] = Field(
        description="Source type of the job description"
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Source URL (for linkedin_url type)",
    )
    fetch_status: Literal["success", "not_applicable"] = Field(
        description="Fetch status for LinkedIn scraping"
    )
    character_count: int = Field(description="Character count of the content")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "550e8400-e29b-41d4-a716-446655440001",
                    "content": "We are seeking a Senior Python Developer...",
                    "source_type": "manual",
                    "source_url": None,
                    "fetch_status": "not_applicable",
                    "character_count": 1543,
                },
                {
                    "job_id": "550e8400-e29b-41d4-a716-446655440002",
                    "content": "About the job\n\nWe are looking for a talented...",
                    "source_type": "linkedin_url",
                    "source_url": "https://www.linkedin.com/jobs/view/123456789/",
                    "fetch_status": "success",
                    "character_count": 2341,
                },
            ]
        }
    }


class JobSubmissionErrorResponse(BaseModel):
    """Error response for job submission failures."""

    success: bool = Field(default=False, description="Success status")
    error: str = Field(description="Error type/code")
    message: str = Field(description="Human-readable error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
    fallback: str = Field(
        default="manual_input",
        description="Suggested fallback method",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "scraping_failed",
                "message": "Failed to fetch job description. Please try manual input.",
                "details": "Request timeout after 15 seconds",
                "fallback": "manual_input",
            }
        }
    }
