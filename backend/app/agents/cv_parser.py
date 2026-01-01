"""CVParser Agent - Extract structured data from Markdown CVs."""

import json
import logging
from typing import Any, Dict

from agent_framework.azure import AzureOpenAIChatClient

logger = logging.getLogger(__name__)


class CVParserAgent:
    """
    Agent that extracts structured data from Markdown CVs.

    Extracts:
    - Candidate information
    - Skills (technical and soft)
    - Work experience with dates
    - Education history
    - Projects and certifications
    - Total years of experience
    """

    SYSTEM_MESSAGE = """You are an expert CV/resume parser. Your task is to extract structured information from Markdown CVs.

Extract and return JSON with these fields:
- candidate_name: Full name
- email: Contact email
- phone: Contact phone (if available)
- location: Current location (if mentioned)
- skills: List of all technical and soft skills mentioned
- total_years_experience: Total years of professional experience (calculate from work history)
- work_experience: List of jobs, each with:
  - company: Company name
  - title: Job title
  - start_date: Start date (YYYY-MM format if available, or year)
  - end_date: End date or "Present"
  - duration_years: Duration in years (calculated)
  - responsibilities: List of key responsibilities/achievements
- education: List of degrees, each with:
  - degree: Degree name (e.g., "Bachelor of Science in Computer Science")
  - institution: School/university name
  - graduation_year: Year of graduation
- certifications: List of certifications
- projects: List of notable projects mentioned

Normalize skill names (e.g., "React.js" → "React", "K8s" → "Kubernetes").
Calculate years of experience accurately from date ranges.
If information is not available, use null or empty lists as appropriate.

Return ONLY valid JSON, no additional text."""

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize CVParser agent.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.client = openai_client
        self.agent = openai_client.create_agent(
            name="CVParser",
            instructions=self.SYSTEM_MESSAGE,
        )
        logger.info("CVParser agent initialized")

    async def parse(self, cv_markdown: str) -> Dict[str, Any]:
        """
        Parse CV Markdown into structured format.

        Args:
            cv_markdown: CV content in Markdown format

        Returns:
            Dictionary with structured CV data

        Raises:
            ValueError: If parsing fails or returns invalid JSON
        """
        logger.info(f"Parsing CV (length: {len(cv_markdown)})")

        try:
            # Create prompt
            prompt = f"Parse this CV:\n\n{cv_markdown}"

            # Run agent
            response = await self.agent.run(prompt)

            # Extract response text
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Parse JSON response
            parsed_data = json.loads(response_text)

            # Validate required fields
            required_fields = ["skills", "total_years_experience", "work_experience"]
            for field in required_fields:
                if field not in parsed_data or parsed_data.get(field) is None:
                    logger.warning(f"Missing or null field: {field}, adding default")
                    if field in ["skills", "work_experience", "education"]:
                        parsed_data[field] = []
                    elif field == "total_years_experience":
                        parsed_data[field] = 0
                    else:
                        parsed_data[field] = None

            logger.info(
                f"CV parsing complete - Name: {parsed_data.get('candidate_name')}, "
                f"Skills: {len(parsed_data.get('skills', []))}, "
                f"Experience: {parsed_data.get('total_years_experience')} years"
            )

            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response_text if 'response_text' in locals() else 'N/A'}")
            raise ValueError(f"Invalid JSON response from CVParser agent: {e}")
        except Exception as e:
            logger.error(f"CVParser agent failed: {e}")
            raise
