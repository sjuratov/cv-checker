"""Models package initialization."""

from app.models.domain import AnalysisResult, CVDocument, JobDescription, SkillMatch
from app.models.requests import AnalyzeRequest
from app.models.responses import (
    AnalyzeResponse,
    ErrorResponse,
    HealthCheckResponse,
    SkillMatchResponse,
)

__all__ = [
    # Domain models
    "AnalysisResult",
    "CVDocument",
    "JobDescription",
    "SkillMatch",
    # Request models
    "AnalyzeRequest",
    # Response models
    "AnalyzeResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "SkillMatchResponse",
]
