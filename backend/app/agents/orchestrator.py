"""Orchestrator - Sequential workflow coordination using Microsoft Agent Framework."""

import logging
from typing import Dict, Any, AsyncIterator, Optional
import json

from agent_framework.azure import AzureOpenAIChatClient

from app.agents.analyzer import HybridScoringAgent
from app.agents.cv_parser import CVParserAgent
from app.agents.job_parser import JobParserAgent
from app.agents.report_generator import ReportGeneratorAgent
from app.models.domain import AnalysisResult, SkillMatch

logger = logging.getLogger(__name__)


class CVCheckerOrchestrator:
    """
    Orchestrates the CV checking workflow using sequential agent execution.

    Workflow:
    1. JobParser → Extract job requirements
    2. CVParser → Extract CV data
    3. Analyzer → Hybrid scoring (deterministic + LLM)
    4. ReportGenerator → Create recommendations

    Implements ADR-001: Sequential orchestration pattern
    """

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize orchestrator with all agents.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.openai_client = openai_client

        # Initialize all agents
        self.job_parser = JobParserAgent(openai_client)
        self.cv_parser = CVParserAgent(openai_client)
        self.analyzer = HybridScoringAgent(openai_client)
        self.report_generator = ReportGeneratorAgent(openai_client)

        logger.info("CV Checker Orchestrator initialized with 4 agents")

    async def execute(
        self, cv_markdown: str, job_description: str
    ) -> AnalysisResult:
        """Execute workflow without streaming (backward compatible)."""
        result = None
        async for chunk in self.execute_with_progress(cv_markdown, job_description):
            if chunk.get("type") == "result":
                result = chunk["data"]
        return result

    async def execute_with_progress(
        self, cv_markdown: str, job_description: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute the complete CV analysis workflow with progress updates.

        Args:
            cv_markdown: CV content in Markdown format
            job_description: Job description text

        Yields:
            Progress updates and final result as dict chunks

        Raises:
            Exception: If any agent in the workflow fails
        """
        logger.info("=" * 60)
        logger.info("Starting CV Checker workflow execution")
        logger.info("=" * 60)

        try:
            # Step 1: Parse job description
            logger.info("Step 1/4: Parsing job description...")
            yield {
                "type": "progress",
                "step": 1,
                "total_steps": 4,
                "message": "Parsing job description...",
                "status": "in_progress"
            }
            
            job_requirements = await self.job_parser.parse(job_description)
            logger.info(f"✓ Job parsed - Title: {job_requirements.get('job_title')}")
            
            yield {
                "type": "progress",
                "step": 1,
                "total_steps": 4,
                "message": "Job description parsed",
                "status": "completed"
            }

            # Step 2: Parse CV
            logger.info("Step 2/4: Parsing CV...")
            yield {
                "type": "progress",
                "step": 2,
                "total_steps": 4,
                "message": "Parsing CV...",
                "status": "in_progress"
            }
            
            candidate_profile = await self.cv_parser.parse(cv_markdown)
            logger.info(
                f"✓ CV parsed - Candidate: {candidate_profile.get('candidate_name')}, "
                f"Experience: {candidate_profile.get('total_years_experience')} years"
            )
            
            yield {
                "type": "progress",
                "step": 2,
                "total_steps": 4,
                "message": "CV parsed",
                "status": "completed"
            }

            # Step 3: Analyze compatibility (hybrid scoring)
            logger.info("Step 3/4: Analyzing compatibility...")
            yield {
                "type": "progress",
                "step": 3,
                "total_steps": 4,
                "message": "Analyzing compatibility...",
                "status": "in_progress"
            }
            
            hybrid_score = await self.analyzer.analyze(
                job_description=job_description,
                cv_content=cv_markdown,
                job_requirements=job_requirements,
                candidate_profile=candidate_profile,
            )
            logger.info(
                f"✓ Analysis complete - Score: {hybrid_score.final_score}/100 ({hybrid_score.grade})"
            )
            
            yield {
                "type": "progress",
                "step": 3,
                "total_steps": 4,
                "message": "Compatibility analysis completed",
                "status": "completed"
            }

            # Step 4: Generate recommendations
            logger.info("Step 4/4: Generating recommendations...")
            yield {
                "type": "progress",
                "step": 4,
                "total_steps": 4,
                "message": "Generating recommendations...",
                "status": "in_progress"
            }
            
            report_data = await self.report_generator.generate(
                hybrid_score_dict=hybrid_score.to_dict(),
                job_requirements=job_requirements,
                candidate_profile=candidate_profile,
            )
            logger.info(
                f"✓ Report generated - {len(report_data.get('recommendations', []))} recommendations"
            )
            
            yield {
                "type": "progress",
                "step": 4,
                "total_steps": 4,
                "message": "Recommendations generated",
                "status": "completed"
            }

            # Convert to AnalysisResult domain model
            result = self._build_analysis_result(
                hybrid_score=hybrid_score,
                report_data=report_data,
                job_requirements=job_requirements,
                candidate_profile=candidate_profile,
            )

            logger.info("=" * 60)
            logger.info(f"Workflow complete - Final Score: {result.overall_score}/100")
            logger.info("=" * 60)

            # Yield final result
            yield {
                "type": "result",
                "data": result
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            raise

    def _build_analysis_result(
        self,
        hybrid_score: Any,
        report_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        candidate_profile: Dict[str, Any],
    ) -> AnalysisResult:
        """
        Build AnalysisResult domain model from workflow outputs.

        Args:
            hybrid_score: HybridScore from analyzer
            report_data: Report data from report generator
            job_requirements: Parsed job requirements
            candidate_profile: Parsed candidate profile

        Returns:
            AnalysisResult domain model
        """
        # Build skill matches
        skill_matches = []

        # Add matched skills
        for skill in hybrid_score.deterministic_component.matched_skills:
            skill_matches.append(
                SkillMatch(
                    skill_name=skill,
                    required=True,
                    candidate_has=True,
                    proficiency_level="present",
                    years_experience=None,
                    match_score=1.0,
                )
            )

        # Add missing skills
        for skill in hybrid_score.deterministic_component.missing_skills:
            skill_matches.append(
                SkillMatch(
                    skill_name=skill,
                    required=True,
                    candidate_has=False,
                    proficiency_level=None,
                    years_experience=None,
                    match_score=0.0,
                )
            )

        # Build experience match
        experience_match = {
            "required_years": job_requirements.get("required_years", 0),
            "candidate_years": candidate_profile.get("total_years_experience", 0),
            "alignment_score": hybrid_score.deterministic_component.experience_alignment_percent,
            "match": hybrid_score.deterministic_component.experience_alignment_percent >= 70,
        }

        # Build education match
        education_match = {
            "required": job_requirements.get("education_requirements", "Not specified"),
            "candidate": self._format_education(candidate_profile.get("education", [])),
            "match": True,  # Simplified for now
            "score": 100.0,  # Simplified for now
        }

        # Format recommendations as simple list
        recommendations_list = self.report_generator.format_recommendations_as_list(
            report_data
        )

        # Ensure minimum 5 recommendations
        while len(recommendations_list) < 5:
            recommendations_list.append(
                "Continue developing skills aligned with career goals"
            )

        return AnalysisResult(
            overall_score=hybrid_score.final_score,
            skill_matches=skill_matches,
            experience_match=experience_match,
            education_match=education_match,
            strengths=hybrid_score.strengths[:5],  # Max 5
            gaps=hybrid_score.gaps[:5],  # Max 5
            recommendations=recommendations_list[:10],  # Max 10
            job_title=job_requirements.get("job_title"),
            seniority_level=job_requirements.get("role_type"),
        )

    def _format_education(self, education_list: list) -> str:
        """Format education list into a readable string."""
        if not education_list:
            return "Not specified"

        formatted = []
        for edu in education_list[:2]:  # Show top 2
            degree = edu.get("degree", "Unknown degree")
            institution = edu.get("institution", "Unknown institution")
            formatted.append(f"{degree} from {institution}")

        return "; ".join(formatted)
