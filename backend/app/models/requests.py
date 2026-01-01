"""API request models."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request model for CV analysis."""

    cv_markdown: str = Field(
        ...,
        min_length=100,
        max_length=50000,
        description="CV content in Markdown format",
    )
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Job description text",
    )

    @field_validator("cv_markdown", "job_description")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that content is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "cv_markdown": "# John Doe\n\n## Experience\n\n**Senior Python Developer** (2019-2024)\n- Built scalable APIs with FastAPI\n- Deployed to Azure\n\n## Skills\n- Python (5 years)\n- FastAPI\n- Azure",
                "job_description": "We are seeking a Senior Python Developer with 5+ years of experience in building REST APIs using FastAPI and deploying to cloud platforms like Azure.",
            }
        }
    }


class JobSubmissionRequest(BaseModel):
    """Request model for job submission (manual or LinkedIn URL)."""

    source_type: Literal["manual", "linkedin_url"] = Field(
        ...,
        description="Source type: 'manual' for pasted text, 'linkedin_url' for URL scraping",
    )
    content: Optional[str] = Field(
        default=None,
        max_length=50000,
        description="Job description text (required for manual source type)",
    )
    url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="LinkedIn job posting URL (required for linkedin_url source type)",
    )

    @field_validator("content")
    @classmethod
    def validate_manual_content(cls, v: Optional[str], info) -> Optional[str]:
        """Validate manual content if source_type is manual."""
        # Access source_type from validation context
        data = info.data
        source_type = data.get("source_type")
        
        if source_type == "manual":
            if not v:
                raise ValueError("Content is required for manual source type")
            if len(v.strip()) < 50:
                raise ValueError(
                    f"Job description is too short (minimum 50 characters required). "
                    f"Received {len(v.strip())} characters."
                )
        
        return v.strip() if v else None

    @field_validator("url")
    @classmethod
    def validate_linkedin_url_field(cls, v: Optional[str], info) -> Optional[str]:
        """Validate URL field if source_type is linkedin_url."""
        data = info.data
        source_type = data.get("source_type")
        
        if source_type == "linkedin_url":
            if not v:
                raise ValueError("URL is required for linkedin_url source type")
        
        return v.strip() if v else None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source_type": "manual",
                    "content": "We are seeking a Senior Python Developer with 5+ years of experience...",
                },
                {
                    "source_type": "linkedin_url",
                    "url": "https://www.linkedin.com/jobs/view/123456789/",
                },
            ]
        }
    }
