"""CV Checker service - business logic layer."""

import logging
from typing import Optional

from agent_framework.azure import AzureOpenAIChatClient

from app.agents.orchestrator import CVCheckerOrchestrator
from app.models.domain import AnalysisResult
from app.repositories.analysis import AnalysisRepository

logger = logging.getLogger(__name__)


class CVCheckerService:
    """
    Service layer for CV analysis - storage-agnostic.

    This service orchestrates the CV analysis workflow while being
    independent of the storage mechanism (in-memory v1, Cosmos DB v2+).
    """

    def __init__(
        self,
        repository: AnalysisRepository,
        openai_client: AzureOpenAIChatClient,
    ):
        """
        Initialize CV Checker service.

        Args:
            repository: Analysis repository implementation
            openai_client: Microsoft Agent Framework Azure OpenAI chat client
        """
        self.repository = repository
        self.orchestrator = CVCheckerOrchestrator(openai_client)
        logger.info(
            f"CVCheckerService initialized with {type(repository).__name__} "
            "and AI agent orchestrator"
        )

    async def analyze_cv(
        self, cv_markdown: str, job_description: str
    ) -> AnalysisResult:
        """
        Analyze CV against job description using AI agent workflow.

        Executes sequential workflow:
        1. JobParser Agent - Extract job requirements
        2. CVParser Agent - Extract CV data
        3. Analyzer Agent - Hybrid scoring (deterministic + LLM)
        4. ReportGenerator Agent - Create recommendations

        Args:
            cv_markdown: CV content in Markdown format
            job_description: Job description text

        Returns:
            AnalysisResult with scores and recommendations

        Raises:
            Exception: If agent workflow fails
        """
        logger.info(
            f"Starting CV analysis - CV length: {len(cv_markdown)}, "
            f"JD length: {len(job_description)}"
        )

        try:
            # Execute agent workflow
            result = await self.orchestrator.execute(
                cv_markdown=cv_markdown,
                job_description=job_description,
            )

            # Save (no-op in v1, persists in v2+)
            analysis_id = await self.repository.save(result)
            logger.info(f"Analysis completed and saved with ID: {analysis_id}")

            return result

        except Exception as e:
            logger.error(f"CV analysis failed: {e}", exc_info=True)
            raise

    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """
        Retrieve analysis by ID.

        Args:
            analysis_id: Unique analysis identifier

        Returns:
            AnalysisResult if found, None otherwise
        """
        return await self.repository.get_by_id(analysis_id)

    async def list_recent_analyses(self, limit: int = 10) -> list[AnalysisResult]:
        """
        List recent analyses.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent AnalysisResults
        """
        return await self.repository.list_recent(limit)
