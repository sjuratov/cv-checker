"""Analyzer Agent - Hybrid scoring with deterministic + LLM validation."""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

from agent_framework.azure import AzureOpenAIChatClient

logger = logging.getLogger(__name__)


@dataclass
class DeterministicScore:
    """Deterministic scoring results."""

    skill_match_percent: float
    experience_alignment_percent: float
    total_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_gaps: Dict[str, str]


@dataclass
class LLMScore:
    """LLM semantic scoring results."""

    semantic_match_percent: float
    soft_skills_match_percent: float
    total_score: float
    reasoning: str
    transferable_skills: List[str]
    cultural_fit_notes: str


@dataclass
class HybridScore:
    """Combined hybrid score with full breakdown."""

    final_score: float
    deterministic_component: DeterministicScore
    llm_component: LLMScore
    grade: str
    strengths: List[str]
    gaps: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "final_score": self.final_score,
            "grade": self.grade,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "breakdown": {
                "deterministic": {
                    "weight": "60%",
                    "score": self.deterministic_component.total_score,
                    "skill_match": self.deterministic_component.skill_match_percent,
                    "experience_alignment": self.deterministic_component.experience_alignment_percent,
                    "matched_skills": self.deterministic_component.matched_skills,
                    "missing_skills": self.deterministic_component.missing_skills,
                },
                "llm_semantic": {
                    "weight": "40%",
                    "score": self.llm_component.total_score,
                    "semantic_match": self.llm_component.semantic_match_percent,
                    "soft_skills": self.llm_component.soft_skills_match_percent,
                    "transferable_skills": self.llm_component.transferable_skills,
                    "reasoning": self.llm_component.reasoning,
                },
            },
        }


class DeterministicScorer:
    """Calculate deterministic compatibility metrics."""

    def calculate_skill_match(
        self, required_skills: List[str], candidate_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate skill match percentage using normalized comparison.

        Args:
            required_skills: Required skills from job
            candidate_skills: Candidate's skills

        Returns:
            Tuple of (match_percentage, matched_skills, missing_skills)
        """
        # Normalize to lowercase for comparison
        required_normalized = {s.lower().strip() for s in required_skills if s}
        candidate_normalized = {s.lower().strip() for s in candidate_skills if s}

        if not required_normalized:
            return 100.0, [], []

        # Find exact matches
        matched = required_normalized.intersection(candidate_normalized)
        missing = required_normalized - candidate_normalized

        match_percent = (len(matched) / len(required_normalized)) * 100

        return match_percent, list(matched), list(missing)

    def calculate_experience_alignment(
        self, required_years: int, candidate_years: float
    ) -> Tuple[float, Dict[str, str]]:
        """
        Calculate experience alignment percentage.

        Args:
            required_years: Minimum years required
            candidate_years: Candidate's years of experience

        Returns:
            Tuple of (alignment_percentage, gaps_explanation)
        """
        gaps = {}
        # Handle None values - convert to 0
        required_years = required_years if required_years is not None else 0
        candidate_years = candidate_years if candidate_years is not None else 0
        if candidate_years >= required_years:
            # Over-qualified: 100% if within 2x requirement
            if candidate_years <= required_years * 2:
                alignment = 100.0
            else:
                # Slight penalty for extreme over-qualification
                alignment = max(90.0, 100 - (candidate_years - required_years * 2) * 2)
                gaps["over_qualified"] = (
                    f"Candidate has {candidate_years - required_years:.1f} years beyond requirement"
                )
        else:
            # Under-qualified: linear penalty
            shortage = required_years - candidate_years
            alignment = max(0.0, 100 - (shortage / required_years * 100))
            gaps["under_qualified"] = f"Missing {shortage:.1f} years of experience"

        return alignment, gaps

    def score(
        self, job_requirements: Dict[str, Any], candidate_profile: Dict[str, Any]
    ) -> DeterministicScore:
        """
        Generate deterministic compatibility score.

        Args:
            job_requirements: Parsed job requirements
            candidate_profile: Parsed candidate CV

        Returns:
            DeterministicScore with breakdown
        """
        # Calculate skill match
        skill_match, matched, missing = self.calculate_skill_match(
            job_requirements.get("required_skills", []),
            candidate_profile.get("skills", []),
        )

        # Calculate experience alignment
        exp_align, exp_gaps = self.calculate_experience_alignment(
            job_requirements.get("required_years", 0),
            candidate_profile.get("total_years_experience", 0),
        )

        # Weighted combination: skill match 40%, experience 20% (of total 60%)
        # This gives us skill_match * 0.667 + exp_align * 0.333 within the 60% bucket
        total = (skill_match * 0.667) + (exp_align * 0.333)

        logger.info(
            f"Deterministic score: {total:.2f} "
            f"(skills: {skill_match:.2f}%, experience: {exp_align:.2f}%)"
        )

        return DeterministicScore(
            skill_match_percent=round(skill_match, 2),
            experience_alignment_percent=round(exp_align, 2),
            total_score=round(total, 2),
            matched_skills=matched,
            missing_skills=missing,
            experience_gaps=exp_gaps,
        )


class LLMSemanticValidator:
    """LLM-powered semantic analysis and soft skills evaluation."""

    SYSTEM_MESSAGE = """You are an expert technical recruiter with deep understanding of skill transferability and cultural fit.

Analyze the candidate's CV against job requirements considering:

1. **Semantic Skill Matching**: Identify skills not caught by keyword matching
   - Synonyms and related technologies
   - Transferable skills (e.g., Java → C#, AWS → Azure)
   - Context and depth of experience from project descriptions

2. **Soft Skills & Cultural Fit**: Evaluate intangibles
   - Leadership and collaboration indicators
   - Communication style from CV writing quality
   - Problem-solving approach from achievements
   - Growth mindset and learning ability

Return JSON with:
{
  "semantic_match_percent": <0-100>,
  "soft_skills_match_percent": <0-100>,
  "reasoning": "<brief explanation>",
  "transferable_skills": ["skill1", "skill2"],
  "cultural_fit_notes": "<observations>",
  "strengths": ["strength1", "strength2", "strength3"],
  "gaps": ["gap1", "gap2", "gap3"]
}

Be objective but considerate. Focus on actionable insights."""

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize LLM semantic validator.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.client = openai_client
        self.agent = openai_client.create_agent(
            name="SemanticValidator",
            instructions=self.SYSTEM_MESSAGE,
        )
        logger.info("LLM Semantic Validator initialized")

    async def validate_and_score(
        self,
        job_description: str,
        cv_content: str,
        deterministic_score: DeterministicScore,
    ) -> LLMScore:
        """
        Perform semantic analysis and soft skills evaluation.

        Args:
            job_description: Original job description
            cv_content: Original CV content
            deterministic_score: Pre-calculated deterministic metrics

        Returns:
            LLMScore with semantic and soft skills assessment
        """
        logger.info("Starting LLM semantic validation")

        try:
            # Build prompt with context
            task = f"""**DETERMINISTIC BASELINE**:
- Skill Match: {deterministic_score.skill_match_percent}%
- Matched Skills: {', '.join(deterministic_score.matched_skills) if deterministic_score.matched_skills else 'None'}
- Missing Skills: {', '.join(deterministic_score.missing_skills) if deterministic_score.missing_skills else 'None'}
- Experience Alignment: {deterministic_score.experience_alignment_percent}%

**JOB DESCRIPTION**:
{job_description}

**CANDIDATE CV**:
{cv_content}

Analyze and return JSON only."""

            # Run agent
            response = await self.agent.run(task)

            # Extract and parse response
            response_text = response.content if hasattr(response, 'content') else str(response)
            parsed = json.loads(response_text)

            # Calculate weighted LLM score (semantic 25%, soft 15% of total)
            # Within the 40% LLM bucket: semantic gets 62.5%, soft gets 37.5%
            total = (
                parsed.get("semantic_match_percent", 0) * 0.625
                + parsed.get("soft_skills_match_percent", 0) * 0.375
            )

            logger.info(f"LLM validation complete - Total: {total:.2f}")

            return LLMScore(
                semantic_match_percent=round(parsed.get("semantic_match_percent", 0), 2),
                soft_skills_match_percent=round(parsed.get("soft_skills_match_percent", 0), 2),
                total_score=round(total, 2),
                reasoning=parsed.get("reasoning", ""),
                transferable_skills=parsed.get("transferable_skills", []),
                cultural_fit_notes=parsed.get("cultural_fit_notes", ""),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError(f"Invalid JSON from LLM validator: {e}")
        except Exception as e:
            logger.error(f"LLM validation failed: {e}")
            raise


class HybridScoringAgent:
    """
    Analyzer agent combining deterministic and LLM scoring.

    Implements ADR-003 hybrid scoring:
    - 60% Deterministic (40% skills + 20% experience)
    - 40% LLM (25% semantic + 15% soft skills)
    """

    def __init__(self, openai_client: AzureOpenAIChatClient):
        """
        Initialize hybrid scoring agent.

        Args:
            openai_client: Configured Azure OpenAI chat client from Microsoft Agent Framework
        """
        self.deterministic_scorer = DeterministicScorer()
        self.llm_validator = LLMSemanticValidator(openai_client)
        logger.info("Hybrid Scoring Agent initialized")

    async def analyze(
        self,
        job_description: str,
        cv_content: str,
        job_requirements: Dict[str, Any],
        candidate_profile: Dict[str, Any],
    ) -> HybridScore:
        """
        Generate hybrid compatibility score.

        Args:
            job_description: Original job description text
            cv_content: Original CV markdown
            job_requirements: Parsed job requirements from JobParser
            candidate_profile: Parsed CV data from CVParser

        Returns:
            HybridScore with full breakdown
        """
        logger.info("Starting hybrid scoring analysis")

        # Step 1: Deterministic scoring (60%)
        det_score = self.deterministic_scorer.score(job_requirements, candidate_profile)

        # Step 2: LLM semantic validation (40%)
        llm_score = await self.llm_validator.validate_and_score(
            job_description, cv_content, det_score
        )

        # Step 3: Weighted combination
        final = (det_score.total_score * 0.60) + (llm_score.total_score * 0.40)

        # Step 4: Assign letter grade
        grade = self._calculate_grade(final)

        # Step 5: Compile strengths and gaps
        strengths = self._compile_strengths(det_score, llm_score)
        gaps = self._compile_gaps(det_score, llm_score)

        logger.info(f"Hybrid scoring complete - Final: {final:.2f} ({grade})")

        return HybridScore(
            final_score=round(final, 2),
            deterministic_component=det_score,
            llm_component=llm_score,
            grade=grade,
            strengths=strengths,
            gaps=gaps,
        )

    def _calculate_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _compile_strengths(
        self, det_score: DeterministicScore, llm_score: LLMScore
    ) -> List[str]:
        """Compile strengths from both scoring components."""
        strengths = []

        # From deterministic
        if det_score.matched_skills:
            strengths.append(
                f"Strong match on {len(det_score.matched_skills)} required skills: "
                f"{', '.join(det_score.matched_skills[:5])}"
            )

        if det_score.experience_alignment_percent >= 90:
            strengths.append("Excellent experience level alignment")

        # From LLM - extract from reasoning or use transferable skills
        if llm_score.transferable_skills:
            strengths.append(
                f"Transferable skills identified: {', '.join(llm_score.transferable_skills[:3])}"
            )

        # Ensure at least 3 strengths
        if len(strengths) < 3 and llm_score.reasoning:
            strengths.append(llm_score.reasoning[:200])

        return strengths[:5]  # Max 5 strengths

    def _compile_gaps(
        self, det_score: DeterministicScore, llm_score: LLMScore
    ) -> List[str]:
        """Compile gaps from both scoring components."""
        gaps = []

        # From deterministic
        if det_score.missing_skills:
            gaps.append(
                f"Missing {len(det_score.missing_skills)} required skills: "
                f"{', '.join(det_score.missing_skills[:5])}"
            )

        if det_score.experience_gaps:
            for gap_type, description in det_score.experience_gaps.items():
                gaps.append(description)

        # From LLM
        if llm_score.cultural_fit_notes and "concern" in llm_score.cultural_fit_notes.lower():
            gaps.append(llm_score.cultural_fit_notes[:200])

        return gaps[:5]  # Max 5 gaps
