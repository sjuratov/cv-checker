"""Cosmos DB repository implementation."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from azure.cosmos import ContainerProxy, CosmosClient, exceptions
from azure.identity import DefaultAzureCredential

from app.config import Settings
from app.models.cosmos_models import AnalysisDocument, CVDocument, JobDocument
from app.repositories.analysis import AnalysisRepository, AnalysisResult

logger = logging.getLogger(__name__)


class CosmosDBRepository(AnalysisRepository):
    """
    Cosmos DB implementation of the analysis repository.
    
    Stores CVs, jobs, and analysis results in a single Cosmos DB container
    partitioned by userId.
    """

    def __init__(self, container: ContainerProxy):
        """
        Initialize the Cosmos DB repository.
        
        Args:
            container: Cosmos DB container proxy
        """
        self.container = container
        logger.info("CosmosDBRepository initialized")

    @classmethod
    def create_from_settings(cls, settings: Settings) -> "CosmosDBRepository":
        """
        Factory method to create repository from settings.
        
        Args:
            settings: Application settings
            
        Returns:
            CosmosDBRepository instance
            
        Raises:
            ValueError: If Cosmos DB is not configured
        """
        if not settings.is_cosmos_enabled:
            raise ValueError("Cosmos DB is not configured")

        # Create Cosmos client with appropriate authentication
        connection_str = settings.cosmos_connection_string
        if "AccountKey=" in connection_str:
            # Using connection string with account key
            client = CosmosClient.from_connection_string(connection_str)
        else:
            # Using Azure AD authentication
            credential = DefaultAzureCredential()
            client = CosmosClient(connection_str, credential)

        # Get database and container
        database = client.get_database_client(settings.cosmos_database_name)
        container = database.get_container_client(settings.cosmos_container_name)

        logger.info(
            f"Cosmos DB client created: database={settings.cosmos_database_name}, "
            f"container={settings.cosmos_container_name}"
        )

        return cls(container)

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique document ID with prefix."""
        return f"{prefix}-{uuid.uuid4()}"

    async def create_cv(self, user_id: str, content: str) -> str:
        """
        Store a CV document in Cosmos DB.
        
        Args:
            user_id: User ID (partition key)
            content: CV content in markdown
            
        Returns:
            CV document ID
        """
        cv_doc = CVDocument(
            id=self._generate_id("cv"),
            userId=user_id,
            content=content,
            characterCount=len(content),
        )

        try:
            self.container.create_item(body=cv_doc.model_dump(mode="json"))
            logger.info(f"Created CV document: {cv_doc.id} for user: {user_id}")
            return cv_doc.id
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create CV document: {e}")
            raise

    async def create_job(
        self, user_id: str, content: str, source_type: str, source_url: Optional[str] = None
    ) -> str:
        """
        Store a job description document in Cosmos DB.
        
        Args:
            user_id: User ID (partition key)
            content: Job description content
            source_type: Source type (manual or linkedin_url)
            source_url: Optional source URL
            
        Returns:
            Job document ID
        """
        job_doc = JobDocument(
            id=self._generate_id("job"),
            userId=user_id,
            content=content,
            sourceType=source_type,
            sourceUrl=source_url,
            characterCount=len(content),
        )

        try:
            self.container.create_item(body=job_doc.model_dump(mode="json"))
            logger.info(f"Created job document: {job_doc.id} for user: {user_id}")
            return job_doc.id
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create job document: {e}")
            raise

    async def save(self, result: AnalysisResult) -> str:
        """
        Save analysis result to Cosmos DB.
        
        This method is called by the CVCheckerService after analysis completes.
        It stores the analysis result with a default user ID (anonymous).
        
        Args:
            result: Analysis result to save
            
        Returns:
            Analysis document ID
        """
        # Use default user ID for anonymous analyses (v1 doesn't have auth yet)
        user_id = "anonymous"
        
        # Store the analysis result
        analysis_doc = AnalysisDocument(
            id=result.id,  # Use the existing analysis ID
            userId=user_id,
            cvId="",  # Will be set when we add full document storage
            jobId="",  # Will be set when we add full document storage
            overallScore=result.overall_score,
            skillMatches=[match.model_dump() for match in result.skill_matches],
            experienceMatch=result.experience_match,
            educationMatch=result.education_match,
            strengths=result.strengths,
            gaps=result.gaps,
            recommendations=result.recommendations,
        )

        try:
            self.container.create_item(body=analysis_doc.model_dump(mode="json"))
            logger.info(f"Created analysis document: {analysis_doc.id} for user: {user_id}")
            return analysis_doc.id
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create analysis document: {e}")
            raise

    async def create_analysis(
        self,
        user_id: str,
        cv_id: str,
        job_id: str,
        result: AnalysisResult,
    ) -> str:
        """
        Create a complete analysis document with CV and job references.
        
        Args:
            user_id: User ID (partition key)
            cv_id: CV document ID
            job_id: Job document ID
            result: Analysis result
            
        Returns:
            Analysis document ID
        """
        analysis_doc = AnalysisDocument(
            id=self._generate_id("analysis"),
            userId=user_id,
            cvId=cv_id,
            jobId=job_id,
            overallScore=result.overall_score,
            skillMatches=[match.model_dump() for match in result.skill_matches],
            experienceMatch=result.experience_match,
            educationMatch=result.education_match,
            strengths=result.strengths,
            gaps=result.gaps,
            recommendations=result.recommendations,
        )

        try:
            self.container.create_item(body=analysis_doc.model_dump(mode="json"))
            logger.info(f"Created analysis document: {analysis_doc.id} for user: {user_id}")
            return analysis_doc.id
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create analysis document: {e}")
            raise

    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """
        Retrieve analysis by ID.
        
        Note: This requires knowing the userId (partition key).
        For now, this is a placeholder - proper implementation needs partition key.
        
        Args:
            analysis_id: Analysis document ID
            
        Returns:
            AnalysisResult or None if not found
        """
        # This is a placeholder - need to implement with proper partition key handling
        logger.warning("get_by_id not fully implemented - requires partition key")
        return None

    async def list_recent(self, limit: int = 10) -> list[AnalysisResult]:
        """
        List recent analyses (generic method for base class compliance).
        
        Note: This method doesn't use partition key filtering. Use list_analyses() instead.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of recent AnalysisResult objects (limited implementation)
        """
        logger.warning("list_recent is limited - use list_analyses(user_id) for partition-scoped queries")
        return []

    async def list_analyses(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[AnalysisDocument]:
        """
        List analysis documents for a user.
        
        Args:
            user_id: User ID (partition key)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of analysis documents
        """
        try:
            query = """
                SELECT * FROM c 
                WHERE c.userId = @userId AND c.type = @type
                ORDER BY c.createdAt DESC
                OFFSET @offset LIMIT @limit
            """
            parameters = [
                {"name": "@userId", "value": user_id},
                {"name": "@type", "value": "analysis"},
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit},
            ]

            items = list(
                self.container.query_items(
                    query=query,
                    parameters=parameters,
                    partition_key=user_id,
                )
            )

            analyses = [AnalysisDocument(**item) for item in items]
            logger.info(f"Retrieved {len(analyses)} analyses for user: {user_id}")
            return analyses

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to list analyses: {e}")
            raise

    async def get_cv_by_id(self, user_id: str, cv_id: str) -> Optional[CVDocument]:
        """
        Get CV document by ID.
        
        Args:
            user_id: User ID (partition key)
            cv_id: CV document ID
            
        Returns:
            CV document or None
        """
        try:
            item = self.container.read_item(item=cv_id, partition_key=user_id)
            return CVDocument(**item)
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"CV not found: {cv_id} for user: {user_id}")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get CV: {e}")
            raise

    async def get_job_by_id(self, user_id: str, job_id: str) -> Optional[JobDocument]:
        """
        Get job document by ID.
        
        Args:
            user_id: User ID (partition key)
            job_id: Job document ID
            
        Returns:
            Job document or None
        """
        try:
            item = self.container.read_item(item=job_id, partition_key=user_id)
            return JobDocument(**item)
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Job not found: {job_id} for user: {user_id}")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get job: {e}")
            raise

    async def get_analysis_by_id(
        self, user_id: str, analysis_id: str
    ) -> Optional[AnalysisDocument]:
        """
        Get analysis document by ID.
        
        Args:
            user_id: User ID (partition key)
            analysis_id: Analysis document ID
            
        Returns:
            Analysis document or None
        """
        try:
            item = self.container.read_item(item=analysis_id, partition_key=user_id)
            return AnalysisDocument(**item)
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Analysis not found: {analysis_id} for user: {user_id}")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get analysis: {e}")
            raise

    async def delete_cv(self, user_id: str, cv_id: str) -> bool:
        """Delete CV document."""
        try:
            self.container.delete_item(item=cv_id, partition_key=user_id)
            logger.info(f"Deleted CV: {cv_id} for user: {user_id}")
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete CV: {e}")
            raise

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """Delete job document."""
        try:
            self.container.delete_item(item=job_id, partition_key=user_id)
            logger.info(f"Deleted job: {job_id} for user: {user_id}")
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete job: {e}")
            raise

    async def delete_analysis(self, user_id: str, analysis_id: str) -> bool:
        """Delete analysis document."""
        try:
            self.container.delete_item(item=analysis_id, partition_key=user_id)
            logger.info(f"Deleted analysis: {analysis_id} for user: {user_id}")
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete analysis: {e}")
            raise
