"""FastAPI application for CV Checker."""

import logging
from contextlib import asynccontextmanager
from time import time

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.config import Settings, get_settings
from app.models.requests import AnalyzeRequest
from app.models.responses import (
    AnalyzeResponse,
    ErrorResponse,
    HealthCheckResponse,
    SkillMatchResponse,
)
from app.repositories.analysis import AnalysisRepository, InMemoryAnalysisRepository
from app.services.cv_checker import CVCheckerService
from app.utils.azure_openai import get_openai_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("CV Checker API starting up...")
    settings = get_settings()
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Azure OpenAI endpoint: {settings.azure_openai_endpoint}")

    yield

    # Shutdown
    logger.info("CV Checker API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="CV Checker API",
    description="AI-powered CV analysis and job matching using Microsoft Agent Framework",
    version=__version__,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Get settings
settings = get_settings()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_repository() -> AnalysisRepository:
    """
    Get analysis repository instance.

    Returns in-memory repo for v1, will return Cosmos repo for v2+.
    """
    return InMemoryAnalysisRepository()


def get_service(
    repository: AnalysisRepository = Depends(get_repository),
) -> CVCheckerService:
    """
    Get CV Checker service instance.

    Args:
        repository: Analysis repository

    Returns:
        CVCheckerService instance
    """
    openai_client = get_openai_client()
    return CVCheckerService(repository, openai_client)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom handler for Pydantic validation errors.

    Args:
        request: Request object
        exc: Validation exception

    Returns:
        JSON error response
    """
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {"errors": exc.errors()},
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler.

    Args:
        request: Request object
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"error_type": type(exc).__name__},
        },
    )


# API Endpoints


@app.get(
    "/api/v1/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running and healthy",
    tags=["System"],
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        HealthCheckResponse with service status and version
    """
    try:
        # Test Azure OpenAI client initialization
        client = get_openai_client()
        azure_openai_status = "connected"
    except Exception as e:
        logger.error(f"Azure OpenAI health check failed: {e}")
        azure_openai_status = "unavailable"

    return HealthCheckResponse(
        status="healthy" if azure_openai_status == "connected" else "degraded",
        version=__version__,
        service="cv-checker-api",
        azure_openai=azure_openai_status
    )


@app.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze CV against job description",
    description="Submit a CV and job description to receive detailed matching analysis",
    responses={
        200: {
            "description": "Successful analysis",
            "model": AnalyzeResponse,
        },
        400: {
            "description": "Invalid request (e.g., empty CV or job description)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error (e.g., AI service failure)",
            "model": ErrorResponse,
        },
    },
    tags=["Analysis"],
)
async def analyze_cv(
    request: AnalyzeRequest,
    service: CVCheckerService = Depends(get_service),
) -> AnalyzeResponse:
    """
    Analyze CV against job description using AI agents.

    This endpoint orchestrates a multi-agent workflow to:
    1. Parse job requirements
    2. Parse CV content
    3. Perform comparative analysis
    4. Generate recommendations

    Args:
        request: AnalyzeRequest with CV and job description
        service: CV Checker service instance

    Returns:
        AnalyzeResponse with comprehensive matching results

    Raises:
        HTTPException: On validation or processing errors
    """
    start_time = time()

    try:
        logger.info(
            f"Starting CV analysis - CV length: {len(request.cv_markdown)}, "
            f"JD length: {len(request.job_description)}"
        )

        # Execute analysis workflow
        analysis_result = await service.analyze_cv(
            cv_markdown=request.cv_markdown,
            job_description=request.job_description,
        )

        # Convert internal model to API response
        response = AnalyzeResponse(
            analysis_id=analysis_result.id,
            overall_score=analysis_result.overall_score,
            skill_matches=[
                SkillMatchResponse(**match.model_dump())
                for match in analysis_result.skill_matches
            ],
            experience_match=analysis_result.experience_match,
            education_match=analysis_result.education_match,
            strengths=analysis_result.strengths,
            gaps=analysis_result.gaps,
            recommendations=analysis_result.recommendations,
        )

        elapsed = time() - start_time
        logger.info(
            f"Analysis completed successfully in {elapsed:.2f}s - "
            f"Score: {response.overall_score}"
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "details": {"field": "unknown"},
            },
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AnalysisError",
                "message": "Failed to complete CV analysis",
                "details": {"error_type": type(e).__name__},
            },
        )


# Root endpoint
@app.get(
    "/",
    include_in_schema=False,
)
async def root():
    """Root endpoint redirect to docs."""
    return {
        "message": "CV Checker API",
        "version": __version__,
        "docs": "/api/v1/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
