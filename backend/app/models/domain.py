"""Domain models for CV Checker - Cosmos DB ready."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    """Individual skill matching result."""

    skill_name: str = Field(description="Name of the skill")
    required: bool = Field(description="Whether this skill is required for the job")
    candidate_has: bool = Field(description="Whether the candidate has this skill")
    proficiency_level: Optional[str] = Field(
        default=None,
        description="Proficiency level: beginner, intermediate, advanced",
    )
    years_experience: Optional[float] = Field(
        default=None,
        description="Years of experience with this skill",
    )
    match_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Match score for this skill (0.0 to 1.0)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "skill_name": "Python",
                "required": True,
                "candidate_has": True,
                "proficiency_level": "advanced",
                "years_experience": 5.0,
                "match_score": 1.0,
            }
        }
    }


class AnalysisResult(BaseModel):
    """Complete CV analysis result - Cosmos DB ready."""

    # Cosmos DB metadata (unused in v1, ready for v2)
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique analysis identifier",
    )
    partition_key: str = Field(
        default="analysis",
        alias="partitionKey",
        description="Cosmos DB partition key",
    )
    document_type: str = Field(
        default="cv_analysis",
        description="Document type for Cosmos DB",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Analysis creation timestamp",
    )

    # Analysis data
    overall_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall match score (0-100)",
    )
    skill_matches: list[SkillMatch] = Field(
        default_factory=list,
        description="Detailed skill matching results",
    )
    experience_match: dict[str, Any] = Field(
        default_factory=dict,
        description="Experience level analysis",
    )
    education_match: dict[str, Any] = Field(
        default_factory=dict,
        description="Education requirements analysis",
    )

    # Recommendations
    strengths: list[str] = Field(
        default_factory=list,
        description="Candidate strengths for this role",
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Identified skill/experience gaps",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable recommendations",
    )

    # Context (for future filtering/search)
    job_title: Optional[str] = Field(
        default=None,
        description="Job title from the description",
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry sector",
    )
    seniority_level: Optional[str] = Field(
        default=None,
        description="Seniority level: entry, mid, senior",
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "partitionKey": "analysis",
                "document_type": "cv_analysis",
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
                    "Strong Python experience",
                    "Cloud architecture skills",
                ],
                "gaps": ["Kubernetes experience needed"],
                "recommendations": ["Consider Kubernetes certification"],
            }
        },
    }


class JobDescription(BaseModel):
    """Job description document - Cosmos DB ready."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique job description identifier",
    )
    partition_key: str = Field(
        default="job_description",
        alias="partitionKey",
        description="Cosmos DB partition key",
    )
    document_type: str = Field(
        default="job_description",
        description="Document type for Cosmos DB",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    # Job data
    title: str = Field(description="Job title")
    company: Optional[str] = Field(default=None, description="Company name")
    description_text: str = Field(description="Full job description text")
    required_skills: list[str] = Field(
        default_factory=list,
        description="Required skills",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Preferred skills",
    )
    experience_years: Optional[int] = Field(
        default=None,
        description="Required years of experience",
    )
    education_level: Optional[str] = Field(
        default=None,
        description="Required education level",
    )

    # Metadata for future search
    industry: Optional[str] = Field(default=None, description="Industry sector")
    location: Optional[str] = Field(default=None, description="Job location")
    salary_range: Optional[str] = Field(default=None, description="Salary range")

    model_config = {"populate_by_name": True}


class CVDocument(BaseModel):
    """CV document - Cosmos DB ready."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique CV identifier",
    )
    partition_key: str = Field(
        default="cv_document",
        alias="partitionKey",
        description="Cosmos DB partition key",
    )
    document_type: str = Field(
        default="cv_document",
        description="Document type for Cosmos DB",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    # CV data
    candidate_name: Optional[str] = Field(default=None, description="Candidate name")
    email: Optional[str] = Field(default=None, description="Contact email")
    markdown_content: str = Field(description="CV content in Markdown format")
    skills: list[str] = Field(default_factory=list, description="Extracted skills")
    experience_years: Optional[float] = Field(
        default=None,
        description="Total years of experience",
    )
    education: list[dict[str, str]] = Field(
        default_factory=list,
        description="Education history",
    )
    work_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Work experience",
    )

    model_config = {"populate_by_name": True}
