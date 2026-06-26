"""Tests for the data normalizer."""

import pytest
from scripts.core.models import Opportunity, WorkMode
from scripts.core.normalizer import normalize, _infer_work_mode, _infer_category, _infer_domains


def test_work_mode_remote():
    assert _infer_work_mode("Remote India") == WorkMode.REMOTE.value


def test_work_mode_hybrid():
    assert _infer_work_mode("Hybrid - Bengaluru") == WorkMode.HYBRID.value


def test_work_mode_onsite():
    assert _infer_work_mode("Bengaluru, India") == WorkMode.ONSITE.value


def test_infer_category_internship():
    assert _infer_category("Software Intern", "", "") == "internship"


def test_infer_category_hackathon():
    assert _infer_category("Smart India Hackathon 2025", "", "") == "hackathon"


def test_infer_category_fellowship():
    assert _infer_category("MLH Fellowship 2025", "", "") == "fellowship"


def test_infer_domains_ai():
    domains = _infer_domains("Machine Learning Intern", "work with NLP and deep learning")
    assert "ai-ml" in domains


def test_infer_domains_frontend():
    domains = _infer_domains("React Developer", "build with React and Angular")
    assert "frontend" in domains


def test_normalize_cleans_whitespace():
    opp = Opportunity(title="  SWE  Intern  ", company="  Google  ", location="Bengaluru")
    normalized = normalize(opp)
    assert normalized.title == "SWE Intern"
    assert normalized.company == "Google"


def test_normalize_sets_work_mode():
    opp = Opportunity(title="Intern", company="X", location="Remote - India")
    normalize(opp)
    assert opp.work_mode == WorkMode.REMOTE.value


def test_normalize_detects_india():
    opp = Opportunity(title="Intern", company="X", location="Bengaluru, India")
    normalize(opp)
    assert opp.is_india is True
