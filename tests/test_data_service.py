"""Tests for the recruiting data-access layer."""

import pytest

from recruiting_agent import data_service
from recruiting_agent.recruiting_records import CANDIDATES

CANDIDATE_ID = "CAND-12853"


@pytest.fixture
def restore_skills():
    original = list(CANDIDATES[CANDIDATE_ID]["skills"])
    yield
    CANDIDATES[CANDIDATE_ID]["skills"] = original


def test_add_candidate_skill_persists_to_source_of_truth(restore_skills):
    result = data_service.add_candidate_skill(CANDIDATE_ID, "Rust")

    assert result == {
        "updated": True,
        "found": True,
        "skills": data_service.fetch_skills(CANDIDATE_ID),
    }
    assert "Rust" in data_service.fetch_skills(CANDIDATE_ID)


def test_add_candidate_skill_is_idempotent(restore_skills):
    data_service.add_candidate_skill(CANDIDATE_ID, "Rust")

    result = data_service.add_candidate_skill(CANDIDATE_ID, "Rust")

    assert result["updated"] is False
    assert data_service.fetch_skills(CANDIDATE_ID).count("Rust") == 1


def test_add_candidate_skill_unknown_candidate():
    assert data_service.add_candidate_skill("CAND-00000", "Rust") == {
        "updated": False,
        "found": False,
    }
