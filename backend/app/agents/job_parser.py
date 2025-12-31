"""JobParser Agent - Extract structured data from job descriptions."""

import json
import logging
from typing import Any, Dict

from agent_framework.azure import AzureOpenAIChatClient

logger = logging.getLogger(__name__)


class JobParserAgent:
    """
    Agent that extracts structured requirements from job descriptions.

    Extracts:
    - Job title, company, location
    - Required skills (technical + soft)
    - Preferred skills
    - Experience requirements
    - Education requirements
    - Key responsibilities
    """

    SYSTEM_MESSAGE = """You are an expert job description parser. Your task is to extract structured information from job postings.

Extract and return JSON with these fields:
- job_title: The job title/position
- company: Company name (if mentioned)
- location: Job location (if mentioned)
- required_skills: List of required technical and soft skills
- preferred_skills: List of preferred/nice-to-have skills
- required_years: Minimum years of experience required (number, or null if not specified)
- education_requirements: Education level required (e.g., "Bachelor's in Computer Science")
- key_responsibilities: List of main job responsibilities
- role_type: Seniority level - one of: "entry", "mid", "senior", "lead", "principal"

Be thorough but concise. Normalize skill names (e.g., "React.js" → "React", "K8s" → "Kubernetes").
If information is not available, use null or empty lists as appropriate.

Return ONLY valid JSON, no additional text."""

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize JobParser agent.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.client = openai_client
        self.agent = openai_client.create_agent(
            name="JobParser",
            instructions=self.SYSTEM_MESSAGE,
        )
        logger.info("JobParser agent initialized")

    async def parse(self, job_description: str) -> Dict[str, Any]:
        """
        Parse job description into structured format.

        Args:
            job_description: Raw job description text

        Returns:
            Dictionary with structured job requirements

        Raises:
            ValueError: If parsing fails or returns invalid JSON
        """
        logger.info(f"Parsing job description (length: {len(job_description)})")

        try:
            # Create prompt
            prompt = f"Parse this job description:\n\n{job_description}"

            # Run agent
            response = await self.agent.run(prompt)

            # Extract response text
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Parse JSON response
            parsed_data = json.loads(response_text)

            # Validate required fields
            required_fields = ["job_title", "required_skills", "required_years", "role_type"]
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"Missing required field: {field}, adding default")
                    if field == "required_skills":
                        parsed_data[field] = []
                    elif field == "required_years":
                        parsed_data[field] = 0
                    elif field == "role_type":
                        parsed_data[field] = "mid"
                    else:
                        parsed_data[field] = None

            logger.info(
                f"Job parsing complete - Title: {parsed_data.get('job_title')}, "
                f"Skills: {len(parsed_data.get('required_skills', []))}"
            )

            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response_text if 'response_text' in locals() else 'N/A'}")
            raise ValueError(f"Invalid JSON response from JobParser agent: {e}")
        except Exception as e:
            logger.error(f"JobParser agent failed: {e}")
            raise
