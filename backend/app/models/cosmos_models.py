"""Pydantic models for Cosmos DB documents."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Document type enumeration."""

    CV = "cv"
    JOB = "job"
    ANALYSIS = "analysis"


class BaseCosmosDocument(BaseModel):
    """Base model for all Cosmos DB documents."""

    id: str = Field(..., description="Unique document identifier")
    userId: str = Field(..., description="User ID (partition key)")
    type: DocumentType = Field(..., description="Document type")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "cv-550e8400-e29b-41d4-a716-446655440000",
                "userId": "user-abc123def456",
                "type": "cv",
                "createdAt": "2026-01-01T12:00:00Z",
                "updatedAt": "2026-01-01T12:00:00Z",
            }
        }
    }


class CVDocument(BaseCosmosDocument):
    """CV document model for Cosmos DB."""

    type: DocumentType = Field(default=DocumentType.CV, description="Document type (cv)")
    filename: str = Field(..., description="Original CV filename")
    content: str = Field(..., description="CV content in markdown format")
    characterCount: int = Field(..., description="Character count of CV content")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "cv-550e8400-e29b-41d4-a716-446655440000",
                "userId": "user-abc123def456",
                "type": "cv",
                "filename": "john_doe_resume.pdf",
                "content": "# John Doe\n\n## Experience\n...",
                "characterCount": 1543,
                "createdAt": "2026-01-01T12:00:00Z",
                "updatedAt": "2026-01-01T12:00:00Z",
            }
        }
    }


class JobDocument(BaseCosmosDocument):
    """Job description document model for Cosmos DB."""

    type: DocumentType = Field(default=DocumentType.JOB, description="Document type (job)")
    title: str = Field(..., description="Job title extracted from content")
    content: str = Field(..., description="Job description content")
    sourceType: str = Field(..., description="Source type: manual or linkedin_url")
    sourceUrl: Optional[str] = Field(default=None, description="Source URL if scraped from LinkedIn")
    characterCount: int = Field(..., description="Character count of job content")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "job-550e8400-e29b-41d4-a716-446655440001",
                "userId": "user-abc123def456",
                "type": "job",
                "title": "Senior Python Developer",
                "content": "Senior Python Developer needed...",
                "sourceType": "linkedin_url",
                "sourceUrl": "https://www.linkedin.com/jobs/view/123456789/",
                "characterCount": 2341,
                "createdAt": "2026-01-01T12:00:00Z",
                "updatedAt": "2026-01-01T12:00:00Z",
            }
        }
    }


class SkillMatch(BaseModel):
    """Skill match data."""

    skill_name: str
    required: bool
    candidate_has: bool
    proficiency_level: Optional[str] = None
    years_experience: Optional[float] = None
    match_score: float


class AnalysisDocument(BaseCosmosDocument):
    """Analysis result document model for Cosmos DB."""

    type: DocumentType = Field(default=DocumentType.ANALYSIS, description="Document type (analysis)")
    cvId: str = Field(default="", description="Reference to CV document ID (deprecated, use cvMarkdown)")
    jobId: str = Field(default="", description="Reference to job document ID (deprecated, use jobDescription)")
    cvMarkdown: str = Field(..., description="Full CV content in Markdown format")
    jobDescription: str = Field(..., description="Full job description text")
    sourceType: str = Field(default="manual", description="Job source type: manual or linkedin_url")
    sourceUrl: Optional[str] = Field(default=None, description="LinkedIn URL if job was scraped")
    overallScore: float = Field(..., ge=0.0, le=100.0, description="Overall match score (0-100)")
    skillMatches: list[SkillMatch] = Field(default_factory=list, description="Skill matching results")
    experienceMatch: dict[str, Any] = Field(default_factory=dict, description="Experience match data")
    educationMatch: dict[str, Any] = Field(default_factory=dict, description="Education match data")
    strengths: list[str] = Field(default_factory=list, description="Candidate strengths")
    gaps: list[str] = Field(default_factory=list, description="Identified gaps")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "analysis-550e8400-e29b-41d4-a716-446655440002",
                "userId": "user-abc123def456",
                "type": "analysis",
                "cvId": "cv-550e8400-e29b-41d4-a716-446655440000",
                "jobId": "job-550e8400-e29b-41d4-a716-446655440001",
                "overallScore": 85.5,
                "skillMatches": [],
                "experienceMatch": {},
                "educationMatch": {},
                "strengths": ["Strong Python expertise"],
                "gaps": ["Limited Kubernetes experience"],
                "recommendations": ["Consider Kubernetes certification"],
                "createdAt": "2026-01-01T12:00:00Z",
                "updatedAt": "2026-01-01T12:00:00Z",
            }
        }
    }
