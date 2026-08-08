"""Regression tests for the score_candidate candidate-profile guard."""

import os
import unittest
from unittest import mock

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from recruiting_agent import recruiting_agent as agent
from recruiting_agent.recruiting_agent import (
    CandidateScore,
    RubricBreakdown,
    build_candidate_profile,
    score_candidate,
)

JOB = {
    "job_id": "JOB-10001",
    "title": "Senior Data Scientist",
    "required_skills": ["Python", "SQL", "Spark"],
    "min_years_experience": 5,
    "description": "Build and ship production machine learning systems.",
}


class ScoreCandidateProfileGuardTest(unittest.TestCase):
    def test_stub_profile_is_not_scored(self):
        with mock.patch.object(agent, "_scoring_llm") as scoring_llm, \
                mock.patch.object(agent.data_service, "get_profile_from_db",
                                  return_value={"candidate_profile": None}):
            result = score_candidate.invoke(
                {"candidate_profile": {"candidate_id": "CAND-71001"}, "job_description": JOB}
            )
        self.assertIsNone(result["score"])
        self.assertIn("build_candidate_profile", result["error"])
        scoring_llm.invoke.assert_not_called()

    def test_built_profile_is_scored(self):
        profile = build_candidate_profile.invoke({"candidate_id": "CAND-71001"})["candidate_profile"]
        scored = CandidateScore(
            score=82,
            justification="Strong Python and SQL background.",
            rubric_breakdown=RubricBreakdown(experience=80, skills_match=85, seniority_fit=80),
        )
        with mock.patch.object(agent, "_scoring_llm") as scoring_llm:
            scoring_llm.invoke.return_value = scored
            result = score_candidate.invoke(
                {"candidate_profile": profile, "job_description": JOB}
            )
        self.assertEqual(result["score"], 82)
        self.assertNotIn("error", result)


if __name__ == "__main__":
    unittest.main()
