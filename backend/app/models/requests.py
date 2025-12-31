"""API request models."""

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
