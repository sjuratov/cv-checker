"""FastAPI application for CV Checker."""

import logging
import uuid
from contextlib import asynccontextmanager
from time import time

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import __version__
from app.config import Settings, get_settings
from app.models.requests import AnalyzeRequest, JobSubmissionRequest
from app.models.responses import (
    AnalyzeResponse,
    ErrorResponse,
    HealthCheckResponse,
    JobSubmissionErrorResponse,
    JobSubmissionResponse,
    SkillMatchResponse,
)
from app.repositories.analysis import AnalysisRepository, InMemoryAnalysisRepository
from app.repositories.cosmos_repository import CosmosDBRepository
from app.services.cv_checker import CVCheckerService
from app.services.linkedin_scraper import (
    AntiBotDetected,
    ContentNotFound,
    LinkedInScraperError,
    LinkedInScraperService,
    PageLoadTimeout,
)
from app.utils.azure_openai import get_openai_client
from app.utils.linkedin_validator import is_valid_linkedin_job_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


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
    
    # Initialize LinkedIn scraper service (global instance)
    app.state.linkedin_scraper = LinkedInScraperService()
    await app.state.linkedin_scraper.initialize()
    logger.info("LinkedIn scraper service initialized")
    
    # Initialize Cosmos DB repository (if enabled)
    if settings.is_cosmos_enabled:
        try:
            app.state.cosmos_repository = CosmosDBRepository.create_from_settings(settings)
            logger.info("Cosmos DB repository initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB repository: {e}")
            app.state.cosmos_repository = None
    else:
        logger.info("Cosmos DB not configured, persistence disabled")
        app.state.cosmos_repository = None

    yield

    # Shutdown
    logger.info("CV Checker API shutting down...")
    if hasattr(app.state, 'linkedin_scraper'):
        await app.state.linkedin_scraper.close()
        logger.info("LinkedIn scraper service closed")


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


# Configure CORS middleware (must be before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Dependency injection
def get_repository(request: Request) -> AnalysisRepository:
    """
    Get analysis repository instance.

    Returns Cosmos DB repository if configured, otherwise in-memory repository.
    """
    cosmos_repo = getattr(request.app.state, 'cosmos_repository', None)
    if cosmos_repo is not None:
        logger.debug("Using Cosmos DB repository")
        return cosmos_repo
    
    logger.debug("Using in-memory repository (CosmosDB not configured)")
    return InMemoryAnalysisRepository()


def get_linkedin_scraper(request: Request) -> LinkedInScraperService:
    """
    Get LinkedIn scraper service from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        LinkedInScraperService instance
    """
    return request.app.state.linkedin_scraper


def get_cosmos_repository(request: Request) -> CosmosDBRepository | None:
    """
    Get Cosmos DB repository from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        CosmosDBRepository instance or None if not configured
    """
    return getattr(request.app.state, 'cosmos_repository', None)


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

    # Check Cosmos DB connection (Phase 2)
    cosmos_db_status = "not_configured"
    if settings.is_cosmos_enabled:
        try:
            from azure.cosmos import CosmosClient
            from azure.identity import DefaultAzureCredential
            
            # Check if using Azure AD authentication or connection string
            connection_str = settings.cosmos_connection_string
            if "AccountKey=" in connection_str:
                # Using connection string with account key
                client = CosmosClient.from_connection_string(connection_str)
            else:
                # Using Azure AD authentication (DefaultAzureCredential)
                credential = DefaultAzureCredential()
                client = CosmosClient(connection_str, credential)
            
            # Test connection by listing databases (convert to list to execute)
            _ = list(client.list_databases())
            cosmos_db_status = "connected"
        except Exception as e:
            logger.error(f"Cosmos DB health check failed: {e}")
            cosmos_db_status = "unavailable"

    # Determine overall status
    is_healthy = azure_openai_status == "connected"
    if settings.is_cosmos_enabled:
        is_healthy = is_healthy and cosmos_db_status == "connected"

    return HealthCheckResponse(
        status="healthy" if is_healthy else "degraded",
        version=__version__,
        service="cv-checker-api",
        azure_openai=azure_openai_status,
        cosmos_db=cosmos_db_status if settings.is_cosmos_enabled else "not_configured"
    )


@app.post(
    "/api/v1/jobs",
    response_model=JobSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit job description",
    description="Submit job description via manual text or LinkedIn URL. Rate limit: 5/min, 20/hour per IP (LinkedIn URLs only).",
    responses={
        201: {
            "description": "Job submitted successfully",
            "model": JobSubmissionResponse,
        },
        400: {
            "description": "Invalid request or scraping failed",
            "model": JobSubmissionErrorResponse,
        },
        429: {
            "description": "Rate limit exceeded (LinkedIn URLs only)",
            "model": ErrorResponse,
        },
    },
    tags=["Jobs"],
)
@limiter.limit("5/minute;20/hour", methods=["POST"], error_message="Too many LinkedIn scraping requests. Please try again later.")
async def submit_job(
    request: Request,
    job_request: JobSubmissionRequest,
    scraper: LinkedInScraperService = Depends(get_linkedin_scraper),
) -> JobSubmissionResponse:
    """
    Submit job description (manual text or LinkedIn URL).
    
    **Manual Input Mode:**
    - Provide `source_type: "manual"` and `content` with job description text
    - Minimum 50 characters required
    - No rate limiting applied
    
    **LinkedIn URL Mode:**
    - Provide `source_type: "linkedin_url"` and `url` with LinkedIn job posting URL
    - Server-side scraping using Playwright
    - Rate limited to 5 requests/minute, 20 requests/hour per IP
    - Returns content directly (no database storage in Phase 2)
    
    Args:
        request: FastAPI request object
        job_request: Job submission request (manual or LinkedIn URL)
        scraper: LinkedIn scraper service
        
    Returns:
        JobSubmissionResponse with job ID and content
        
    Raises:
        HTTPException: On validation or scraping errors
    """
    # Manual Input Mode
    if job_request.source_type == "manual":
        content = job_request.content
        
        logger.info(f"Manual job submission - {len(content)} characters")
        
        return JobSubmissionResponse(
            job_id=str(uuid.uuid4()),
            content=content,
            source_type="manual",
            source_url=None,
            fetch_status="not_applicable",
            character_count=len(content),
        )
    
    # LinkedIn URL Mode
    elif job_request.source_type == "linkedin_url":
        url = job_request.url
        
        # Validate LinkedIn URL format
        if not is_valid_linkedin_job_url(url):
            logger.warning(f"Invalid LinkedIn URL format: {url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "invalid_url",
                    "message": "Invalid LinkedIn job URL. Expected format: https://linkedin.com/jobs/view/[ID]",
                    "fallback": "manual_input",
                },
            )
        
        try:
            logger.info(f"Scraping LinkedIn job from URL: {url}")
            content = await scraper.scrape_job_description(url)
            
            # Log warning if content is unusually short (but don't reject)
            if len(content) < 50:
                logger.warning(
                    f"Short LinkedIn content scraped: {len(content)} chars from {url}"
                )
            
            logger.info(f"Successfully scraped {len(content)} characters from {url}")
            
            return JobSubmissionResponse(
                job_id=str(uuid.uuid4()),
                content=content,
                source_type="linkedin_url",
                source_url=url,
                fetch_status="success",
                character_count=len(content),
            )
        
        except PageLoadTimeout as e:
            logger.warning(f"Scraping timeout for {url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "timeout",
                    "message": "Request timeout after 15 seconds. The job posting may not be available.",
                    "details": str(e),
                    "fallback": "manual_input",
                },
            )
        
        except ContentNotFound as e:
            logger.warning(f"Content not found for {url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "content_not_found",
                    "message": "Job description not found. The posting may have been removed or URL is incorrect.",
                    "details": str(e),
                    "fallback": "manual_input",
                },
            )
        
        except AntiBotDetected as e:
            logger.error(f"Anti-bot detected for {url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "anti_bot_detected",
                    "message": "Unable to access LinkedIn at this time. Please try again later or use manual input.",
                    "details": str(e),
                    "fallback": "manual_input",
                },
            )
        
        except LinkedInScraperError as e:
            logger.error(f"Scraping failed for {url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "scraping_failed",
                    "message": "Failed to fetch job description. Please try manual input.",
                    "details": str(e),
                    "fallback": "manual_input",
                },
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
    cosmos_repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
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
        cosmos_repository: Cosmos DB repository (optional)

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

        # Store CV and Job in Cosmos DB if configured
        user_id = "anonymous"  # v1 doesn't have auth yet
        cv_id = ""
        job_id = ""
        
        if cosmos_repository:
            try:
                # Store CV with filename
                cv_id = await cosmos_repository.create_cv(
                    user_id, 
                    request.cv_markdown,
                    filename=request.cv_filename or "resume.pdf"
                )
                logger.info(f"Stored CV: {cv_id}")
                
                # Store Job (determine source type from request or default to manual)
                job_id = await cosmos_repository.create_job(
                    user_id,
                    request.job_description,
                    source_type="manual",
                    source_url=None
                )
                logger.info(f"Stored Job: {job_id}")
            except Exception as e:
                logger.warning(f"Failed to store CV/Job in Cosmos DB: {e}")
                # Continue with analysis even if storage fails

        # Execute analysis workflow
        analysis_result = await service.analyze_cv(
            cv_markdown=request.cv_markdown,
            job_description=request.job_description,
        )

        # Determine source type (will be enhanced when LinkedIn integration is added to analyze endpoint)
        source_type = "manual"
        source_url = None
        
        # If Cosmos DB is configured, create analysis document with full content
        if cosmos_repository:
            try:
                # Create analysis document with CV and job content
                analysis_id = await cosmos_repository.create_analysis(
                    user_id=user_id,
                    cv_markdown=request.cv_markdown,
                    job_description=request.job_description,
                    source_type=source_type,
                    source_url=source_url,
                    result=analysis_result,
                    cv_id=cv_id,
                    job_id=job_id,
                )
                logger.info(f"Created analysis document: {analysis_id}")
                # Update the analysis_result ID to match the Cosmos DB document
                analysis_result.id = analysis_id
            except Exception as e:
                logger.warning(f"Failed to create analysis document in Cosmos DB: {e}")
                # Analysis result is still valid even if Cosmos DB storage fails

        # Convert internal model to API response
        response = AnalyzeResponse(
            analysis_id=analysis_result.id,
            cv_markdown=request.cv_markdown,
            job_description=request.job_description,
            source_type=source_type,
            source_url=source_url,
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


# Phase 2: Cosmos DB Persistence Endpoints


@app.post(
    "/api/v1/cvs",
    status_code=status.HTTP_201_CREATED,
    summary="Store CV",
    description="Store CV content in Cosmos DB (Phase 2)",
    tags=["Persistence"],
)
async def store_cv(
    cv_content: str,
    user_id: str,
    repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
) -> dict:
    """
    Store CV in Cosmos DB.
    
    Args:
        cv_content: CV markdown content
        user_id: User ID (partition key)
        repository: Cosmos DB repository
        
    Returns:
        CV document ID
    """
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cosmos DB not configured",
        )
    
    try:
        cv_id = await repository.create_cv(user_id, cv_content)
        return {"cv_id": cv_id, "user_id": user_id}
    except Exception as e:
        logger.error(f"Failed to store CV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store CV: {str(e)}",
        )


@app.post(
    "/api/v1/jobs/store",
    status_code=status.HTTP_201_CREATED,
    summary="Store job description",
    description="Store job description in Cosmos DB (Phase 2)",
    tags=["Persistence"],
)
async def store_job(
    content: str,
    user_id: str,
    source_type: str,
    source_url: str | None = None,
    repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
) -> dict:
    """
    Store job description in Cosmos DB.
    
    Args:
        content: Job description content
        user_id: User ID (partition key)
        source_type: Source type (manual or linkedin_url)
        source_url: Optional source URL
        repository: Cosmos DB repository
        
    Returns:
        Job document ID
    """
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cosmos DB not configured",
        )
    
    try:
        job_id = await repository.create_job(user_id, content, source_type, source_url)
        return {"job_id": job_id, "user_id": user_id, "source_type": source_type}
    except Exception as e:
        logger.error(f"Failed to store job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store job: {str(e)}",
        )


@app.get(
    "/api/v1/analyses",
    summary="List analyses",
    description="List analysis results for a user (Phase 2)",
    tags=["Persistence"],
)
async def list_analyses(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
) -> dict:
    """
    List analyses for a user.
    
    Args:
        user_id: User ID (partition key)
        limit: Maximum results (default 50)
        offset: Results offset (default 0)
        repository: Cosmos DB repository
        
    Returns:
        List of analysis documents
    """
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cosmos DB not configured",
        )
    
    try:
        analyses = await repository.list_analyses(user_id, limit, offset)
        return {
            "user_id": user_id,
            "count": len(analyses),
            "analyses": [analysis.model_dump() for analysis in analyses],
        }
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}",
        )


@app.get(
    "/api/v1/analyses/{analysis_id}",
    summary="Get analysis by ID",
    description="Retrieve analysis result by ID (Phase 2)",
    tags=["Persistence"],
)
async def get_analysis(
    analysis_id: str,
    user_id: str,
    repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
) -> dict:
    """
    Get analysis by ID.
    
    Args:
        analysis_id: Analysis document ID
        user_id: User ID (partition key)
        repository: Cosmos DB repository
        
    Returns:
        Analysis document
    """
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cosmos DB not configured",
        )
    
    try:
        analysis = await repository.get_analysis_by_id(user_id, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found: {analysis_id}",
            )
        return analysis.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}",
        )


@app.get(
    "/api/v1/history",
    summary="Get analysis history",
    description="Get analysis history with linked CV and Job data for a user",
    tags=["Analysis"],
)
async def get_history(
    user_id: str = "anonymous",
    limit: int = 20,
    repository: CosmosDBRepository | None = Depends(get_cosmos_repository),
) -> dict:
    """
    Get analysis history with linked CV and Job information.
    
    Args:
        user_id: User ID (default: anonymous for v1)
        limit: Maximum number of results (default: 20)
        repository: Cosmos DB repository
        
    Returns:
        List of analysis history items with CV and Job data
    """
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cosmos DB not configured",
        )
    
    try:
        # Fetch analyses for the user
        analyses = await repository.list_analyses(user_id, limit=limit, offset=0)
        
        # Build history with full analysis data including CV and job content
        history_items = []
        for analysis in analyses:
            # Get CV filename and job title from references if available (deprecated)
            cv_filename = "Unknown CV"
            job_title = "Unknown Job"
            
            if analysis.cvId:
                cv_doc = await repository.get_cv_by_id(user_id, analysis.cvId)
                if cv_doc:
                    cv_filename = cv_doc.filename
            
            if analysis.jobId:
                job_doc = await repository.get_job_by_id(user_id, analysis.jobId)
                if job_doc:
                    job_title = job_doc.title
            
            history_items.append({
                "id": analysis.id,
                "timestamp": analysis.createdAt.isoformat(),
                "cvFilename": cv_filename,
                "jobTitle": job_title,
                "score": analysis.overallScore,
                "result": {
                    "analysis_id": analysis.id,
                    "cv_markdown": analysis.cvMarkdown,
                    "job_description": analysis.jobDescription,
                    "source_type": analysis.sourceType,
                    "source_url": analysis.sourceUrl,
                    "overall_score": analysis.overallScore,
                    "skill_matches": analysis.skillMatches,
                    "experience_match": analysis.experienceMatch,
                    "education_match": analysis.educationMatch,
                    "strengths": analysis.strengths,
                    "gaps": analysis.gaps,
                    "recommendations": analysis.recommendations,
                }
            })
        
        logger.info(f"Retrieved {len(history_items)} history items for user: {user_id}")
        return {
            "user_id": user_id,
            "count": len(history_items),
            "history": history_items,
        }
    
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}",
        )
