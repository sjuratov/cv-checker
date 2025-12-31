"""ReportGenerator Agent - Create actionable recommendations and final report."""

import json
import logging
from typing import Any, Dict, List

from agent_framework.azure import AzureOpenAIChatClient

logger = logging.getLogger(__name__)


class ReportGeneratorAgent:
    """
    Agent that generates comprehensive match reports with actionable recommendations.

    Creates:
    - Executive summary
    - Categorized recommendations (Add/Modify/Emphasize/Remove)
    - Priority tagging (High/Medium/Low)
    - Specific, actionable guidance
    """

    SYSTEM_MESSAGE = """You are an expert career coach and technical recruiter. Generate actionable recommendations for CV improvement.

Based on the analysis results, create a comprehensive report with:

1. **Executive Summary**: Brief overview of the match
2. **Recommendations**: Specific, actionable advice categorized by:
   - HIGH priority: Critical gaps that significantly impact match
   - MEDIUM priority: Important improvements that strengthen profile
   - LOW priority: Nice-to-have enhancements

Each recommendation should:
- Be specific and actionable (not vague)
- Explain WHY it matters for this role
- Suggest HOW to implement it

Return JSON:
{
  "executive_summary": "<2-3 sentence overview>",
  "recommendations": [
    {
      "priority": "HIGH|MEDIUM|LOW",
      "category": "ADD_SKILL|MODIFY_CONTENT|EMPHASIZE_EXPERIENCE|REMOVE_CONTENT|RESTRUCTURE",
      "recommendation": "<specific action>",
      "rationale": "<why this matters>"
    }
  ],
  "quick_wins": ["<easy improvement 1>", "<easy improvement 2>"],
  "long_term_development": ["<skill to develop 1>", "<skill to develop 2>"]
}

Ensure at least 5 total recommendations. Be constructive and encouraging."""

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize ReportGenerator agent.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.client = openai_client
        self.agent = openai_client.create_agent(
            name="ReportGenerator",
            instructions=self.SYSTEM_MESSAGE,
        )
        logger.info("ReportGenerator agent initialized")

    async def generate(
        self,
        hybrid_score_dict: Dict[str, Any],
        job_requirements: Dict[str, Any],
        candidate_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations report.

        Args:
            hybrid_score_dict: Hybrid score analysis results
            job_requirements: Parsed job requirements
            candidate_profile: Parsed candidate profile

        Returns:
            Dictionary with recommendations and report
        """
        logger.info(
            f"Generating recommendations for score: {hybrid_score_dict.get('final_score')}"
        )

        try:
            # Build context for report generation
            task = f"""**ANALYSIS RESULTS**:
Final Score: {hybrid_score_dict.get('final_score')}/100 (Grade: {hybrid_score_dict.get('grade')})

Strengths:
{chr(10).join(f"- {s}" for s in hybrid_score_dict.get('strengths', []))}

Gaps:
{chr(10).join(f"- {g}" for g in hybrid_score_dict.get('gaps', []))}

Deterministic Analysis:
- Skill Match: {hybrid_score_dict.get('breakdown', {}).get('deterministic', {}).get('skill_match')}%
- Missing Skills: {', '.join(hybrid_score_dict.get('breakdown', {}).get('deterministic', {}).get('missing_skills', []))}

LLM Analysis:
- Semantic Match: {hybrid_score_dict.get('breakdown', {}).get('llm_semantic', {}).get('semantic_match')}%
- Reasoning: {hybrid_score_dict.get('breakdown', {}).get('llm_semantic', {}).get('reasoning')}

**JOB REQUIREMENTS**:
Title: {job_requirements.get('job_title')}
Required Skills: {', '.join(job_requirements.get('required_skills', []))}
Experience: {job_requirements.get('required_years')} years
Level: {job_requirements.get('role_type')}

**CANDIDATE PROFILE**:
Name: {candidate_profile.get('candidate_name', 'N/A')}
Total Experience: {candidate_profile.get('total_years_experience')} years
Skills: {', '.join(candidate_profile.get('skills', [])[:10])}

Generate actionable recommendations to improve this candidate's match for this role."""

            # Run agent
            response = await self.agent.run(task)

            # Extract and parse response
            response_text = response.content if hasattr(response, 'content') else str(response)
            report_data = json.loads(response_text)

            # Ensure we have required fields
            if "recommendations" not in report_data:
                report_data["recommendations"] = []

            if "executive_summary" not in report_data:
                report_data["executive_summary"] = (
                    f"Candidate scored {hybrid_score_dict.get('final_score')}/100 "
                    f"with grade {hybrid_score_dict.get('grade')}."
                )

            # Ensure minimum recommendations
            if len(report_data["recommendations"]) < 5:
                logger.warning(
                    f"Only {len(report_data['recommendations'])} recommendations generated, "
                    "expected at least 5"
                )

            logger.info(
                f"Report generated with {len(report_data['recommendations'])} recommendations"
            )

            return report_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse report response: {e}")
            raise ValueError(f"Invalid JSON from ReportGenerator: {e}")
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

    def format_recommendations_as_list(
        self, report_data: Dict[str, Any]
    ) -> List[str]:
        """
        Format recommendations as simple list of strings.

        Args:
            report_data: Report data from generate()

        Returns:
            List of formatted recommendation strings
        """
        recommendations = []

        for rec in report_data.get("recommendations", []):
            priority = rec.get("priority", "MEDIUM")
            category = rec.get("category", "GENERAL")
            text = rec.get("recommendation", "")
            rationale = rec.get("rationale", "")

            formatted = f"[{priority}] {text}"
            if rationale:
                formatted += f" - {rationale}"

            recommendations.append(formatted)

        # Add quick wins if available
        if "quick_wins" in report_data:
            for win in report_data["quick_wins"]:
                recommendations.append(f"[QUICK WIN] {win}")

        return recommendations
