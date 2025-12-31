"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.analysis import InMemoryAnalysisRepository
from app.services.cv_checker import CVCheckerService


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def repository():
    """Create a repository instance for testing."""
    return InMemoryAnalysisRepository()


@pytest.fixture
def service(repository):
    """Create a service instance for testing."""
    return CVCheckerService(repository)


@pytest.fixture
def sample_cv_markdown():
    """Sample CV in Markdown format for testing."""
    return """# John Doe

## Contact
- Email: john.doe@example.com
- Phone: +1-234-567-8900

## Professional Summary
Senior Python Developer with 6 years of experience building scalable web applications and APIs.

## Skills
- **Programming Languages**: Python (5 years), JavaScript (3 years)
- **Frameworks**: FastAPI (2 years), Django (3 years), React (2 years)
- **Cloud Platforms**: Azure (2 years), AWS (1 year)
- **Tools**: Docker, Git, CI/CD

## Experience

### Senior Python Developer | Tech Corp | 2021-2024
- Built REST APIs using FastAPI serving 1M+ requests/day
- Deployed microservices to Azure using Docker containers
- Implemented CI/CD pipelines with GitHub Actions
- Led team of 3 junior developers

### Python Developer | StartupCo | 2019-2021
- Developed Django web applications
- Integrated with third-party APIs
- Wrote comprehensive unit tests

## Education
**Master of Science in Computer Science**  
University of Technology, 2019
"""


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """Senior Python Developer

We are seeking a Senior Python Developer with 5+ years of experience to join our growing team.

Requirements:
- 5+ years of Python development experience
- Strong experience with FastAPI or similar web frameworks
- Cloud platform experience (Azure, AWS, or GCP)
- Experience with Docker and containerization
- Bachelor's degree in Computer Science or related field

Preferred:
- Kubernetes experience
- GraphQL knowledge
- Team leadership experience

Responsibilities:
- Design and implement REST APIs
- Deploy and maintain cloud infrastructure
- Mentor junior developers
- Participate in code reviews
"""
