"""Unit tests for Cosmos DB repository."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from azure.cosmos import exceptions

from app.models.cosmos_models import AnalysisDocument, CVDocument, DocumentType, JobDocument
from app.models.domain import AnalysisResult, SkillMatch
from app.repositories.cosmos_repository import CosmosDBRepository


@pytest.fixture
def mock_container():
    """Create mock Cosmos DB container."""
    container = MagicMock()
    container.create_item = MagicMock()
    container.read_item = MagicMock()
    container.delete_item = MagicMock()
    container.query_items = MagicMock()
    return container


@pytest.fixture
def repository(mock_container):
    """Create repository with mock container."""
    return CosmosDBRepository(mock_container)


class TestCosmosDBRepository:
    """Test suite for CosmosDBRepository."""

    def test_generate_id(self, repository):
        """Test ID generation with prefix."""
        cv_id = repository._generate_id("cv")
        assert cv_id.startswith("cv-")
        
        job_id = repository._generate_id("job")
        assert job_id.startswith("job-")
        
        # IDs should be unique
        assert cv_id != job_id

    @pytest.mark.asyncio
    async def test_create_cv_success(self, repository, mock_container):
        """Test successful CV creation."""
        user_id = "user-123"
        content = "# John Doe\n\nExperience: 5 years Python"
        
        cv_id = await repository.create_cv(user_id, content)
        
        assert cv_id.startswith("cv-")
        mock_container.create_item.assert_called_once()
        
        # Verify document structure
        call_args = mock_container.create_item.call_args
        doc = call_args.kwargs['body']
        assert doc['userId'] == user_id
        assert doc['content'] == content
        assert doc['type'] == DocumentType.CV.value
        assert doc['characterCount'] == len(content)

    @pytest.mark.asyncio
    async def test_create_cv_cosmos_error(self, repository, mock_container):
        """Test CV creation with Cosmos DB error."""
        mock_container.create_item.side_effect = exceptions.CosmosHttpResponseError(
            status_code=500, message="Internal error"
        )
        
        with pytest.raises(exceptions.CosmosHttpResponseError):
            await repository.create_cv("user-123", "content")

    @pytest.mark.asyncio
    async def test_create_job_manual(self, repository, mock_container):
        """Test job creation with manual source."""
        user_id = "user-123"
        content = "Senior Python Developer needed"
        source_type = "manual"
        
        job_id = await repository.create_job(user_id, content, source_type)
        
        assert job_id.startswith("job-")
        mock_container.create_item.assert_called_once()
        
        doc = mock_container.create_item.call_args.kwargs['body']
        assert doc['userId'] == user_id
        assert doc['content'] == content
        assert doc['sourceType'] == source_type
        assert doc['sourceUrl'] is None

    @pytest.mark.asyncio
    async def test_create_job_linkedin(self, repository, mock_container):
        """Test job creation with LinkedIn URL."""
        user_id = "user-123"
        content = "Senior Python Developer needed"
        source_type = "linkedin_url"
        source_url = "https://linkedin.com/jobs/view/123"
        
        job_id = await repository.create_job(user_id, content, source_type, source_url)
        
        assert job_id.startswith("job-")
        doc = mock_container.create_item.call_args.kwargs['body']
        assert doc['sourceUrl'] == source_url

    @pytest.mark.asyncio
    async def test_create_analysis(self, repository, mock_container):
        """Test analysis creation."""
        user_id = "user-123"
        cv_id = "cv-456"
        job_id = "job-789"
        
        # Create mock analysis result
        result = AnalysisResult(
            id="analysis-test",
            overall_score=85.5,
            skill_matches=[
                SkillMatch(
                    skill_name="Python",
                    required=True,
                    candidate_has=True,
                    proficiency_level="Expert",
                    years_experience=5.0,
                    match_score=0.95,
                )
            ],
            experience_match={"years": 5, "required": 3},
            education_match={"degree": "Bachelor"},
            strengths=["Strong Python"],
            gaps=["Limited Docker"],
            recommendations=["Learn Docker"],
        )
        
        analysis_id = await repository.create_analysis(user_id, cv_id, job_id, result)
        
        assert analysis_id.startswith("analysis-")
        mock_container.create_item.assert_called_once()
        
        doc = mock_container.create_item.call_args.kwargs['body']
        assert doc['userId'] == user_id
        assert doc['cvId'] == cv_id
        assert doc['jobId'] == job_id
        assert doc['overallScore'] == 85.5
        assert len(doc['skillMatches']) == 1

    @pytest.mark.asyncio
    async def test_get_cv_by_id_success(self, repository, mock_container):
        """Test successful CV retrieval."""
        user_id = "user-123"
        cv_id = "cv-456"
        
        mock_container.read_item.return_value = {
            "id": cv_id,
            "userId": user_id,
            "type": "cv",
            "content": "# CV Content",
            "characterCount": 12,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
        
        cv = await repository.get_cv_by_id(user_id, cv_id)
        
        assert cv is not None
        assert cv.id == cv_id
        assert cv.userId == user_id
        mock_container.read_item.assert_called_once_with(item=cv_id, partition_key=user_id)

    @pytest.mark.asyncio
    async def test_get_cv_by_id_not_found(self, repository, mock_container):
        """Test CV retrieval when not found."""
        mock_container.read_item.side_effect = exceptions.CosmosResourceNotFoundError(
            status_code=404, message="Not found"
        )
        
        cv = await repository.get_cv_by_id("user-123", "cv-nonexistent")
        
        assert cv is None

    @pytest.mark.asyncio
    async def test_get_job_by_id_success(self, repository, mock_container):
        """Test successful job retrieval."""
        user_id = "user-123"
        job_id = "job-456"
        
        mock_container.read_item.return_value = {
            "id": job_id,
            "userId": user_id,
            "type": "job",
            "content": "Job content",
            "sourceType": "manual",
            "sourceUrl": None,
            "characterCount": 11,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
        
        job = await repository.get_job_by_id(user_id, job_id)
        
        assert job is not None
        assert job.id == job_id
        assert job.sourceType == "manual"

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_success(self, repository, mock_container):
        """Test successful analysis retrieval."""
        user_id = "user-123"
        analysis_id = "analysis-456"
        
        mock_container.read_item.return_value = {
            "id": analysis_id,
            "userId": user_id,
            "type": "analysis",
            "cvId": "cv-123",
            "jobId": "job-123",
            "overallScore": 85.5,
            "skillMatches": [],
            "experienceMatch": {},
            "educationMatch": {},
            "strengths": [],
            "gaps": [],
            "recommendations": [],
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
        
        analysis = await repository.get_analysis_by_id(user_id, analysis_id)
        
        assert analysis is not None
        assert analysis.id == analysis_id
        assert analysis.overallScore == 85.5

    @pytest.mark.asyncio
    async def test_list_analyses(self, repository, mock_container):
        """Test listing analyses for a user."""
        user_id = "user-123"
        
        mock_container.query_items.return_value = [
            {
                "id": "analysis-1",
                "userId": user_id,
                "type": "analysis",
                "cvId": "cv-1",
                "jobId": "job-1",
                "overallScore": 85.0,
                "skillMatches": [],
                "experienceMatch": {},
                "educationMatch": {},
                "strengths": [],
                "gaps": [],
                "recommendations": [],
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
            },
            {
                "id": "analysis-2",
                "userId": user_id,
                "type": "analysis",
                "cvId": "cv-2",
                "jobId": "job-2",
                "overallScore": 75.0,
                "skillMatches": [],
                "experienceMatch": {},
                "educationMatch": {},
                "strengths": [],
                "gaps": [],
                "recommendations": [],
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
            },
        ]
        
        analyses = await repository.list_analyses(user_id, limit=10, offset=0)
        
        assert len(analyses) == 2
        assert analyses[0].id == "analysis-1"
        assert analyses[1].id == "analysis-2"
        mock_container.query_items.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_cv_success(self, repository, mock_container):
        """Test successful CV deletion."""
        result = await repository.delete_cv("user-123", "cv-456")
        
        assert result is True
        mock_container.delete_item.assert_called_once_with(
            item="cv-456", partition_key="user-123"
        )

    @pytest.mark.asyncio
    async def test_delete_cv_not_found(self, repository, mock_container):
        """Test CV deletion when not found."""
        mock_container.delete_item.side_effect = exceptions.CosmosResourceNotFoundError(
            status_code=404, message="Not found"
        )
        
        result = await repository.delete_cv("user-123", "cv-nonexistent")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_job_success(self, repository, mock_container):
        """Test successful job deletion."""
        result = await repository.delete_job("user-123", "job-456")
        
        assert result is True
        mock_container.delete_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_analysis_success(self, repository, mock_container):
        """Test successful analysis deletion."""
        result = await repository.delete_analysis("user-123", "analysis-456")
        
        assert result is True
        mock_container.delete_item.assert_called_once()


class TestCosmosDBRepositoryFactory:
    """Test factory method for creating repository."""

    @patch("app.repositories.cosmos_repository.CosmosClient.from_connection_string")
    def test_create_from_settings_with_account_key(self, mock_client_class):
        """Test repository creation with connection string."""
        from app.config import Settings
        
        # Mock settings
        settings = Mock(spec=Settings)
        settings.is_cosmos_enabled = True
        settings.cosmos_connection_string = "AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test123=="
        settings.cosmos_database_name = "test-db"
        settings.cosmos_container_name = "test-container"
        
        # Mock Cosmos client chain
        mock_client = MagicMock()
        mock_database = MagicMock()
        mock_container = MagicMock()
        
        mock_client_class.return_value = mock_client
        mock_client.get_database_client.return_value = mock_database
        mock_database.get_container_client.return_value = mock_container
        
        # Create repository
        repo = CosmosDBRepository.create_from_settings(settings)
        
        assert repo is not None
        assert repo.container == mock_container
        mock_client_class.assert_called_once_with(settings.cosmos_connection_string)

    def test_create_from_settings_not_enabled(self):
        """Test repository creation when Cosmos DB not enabled."""
        from app.config import Settings
        
        settings = Mock(spec=Settings)
        settings.is_cosmos_enabled = False
        
        with pytest.raises(ValueError, match="Cosmos DB is not configured"):
            CosmosDBRepository.create_from_settings(settings)
