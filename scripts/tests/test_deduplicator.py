"""Tests for the deduplication engine."""

from scripts.core.deduplicator import _is_duplicate, _jaccard, deduplicate
from scripts.core.models import Opportunity


def test_jaccard_identical():
    assert _jaccard("software engineer", "software engineer") == 1.0


def test_jaccard_partial():
    score = _jaccard("software engineer intern", "software engineer")
    assert 0.5 < score < 1.0


def test_jaccard_disjoint():
    assert _jaccard("apple mango", "cat dog") == 0.0


def test_exact_url_duplicate():
    a = Opportunity(title="SWE Intern", company="Google", location="Bengaluru",
                    apply_link="https://careers.google.com/jobs/123")
    b = Opportunity(title="Software Intern", company="Google", location="India",
                    apply_link="https://careers.google.com/jobs/123")
    assert _is_duplicate(a, b) is True


def test_same_fingerprint_duplicate():
    a = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    b = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    assert _is_duplicate(a, b) is True


def test_different_company_not_duplicate():
    a = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    b = Opportunity(title="SWE Intern", company="Microsoft", location="Bengaluru")
    assert _is_duplicate(a, b) is False


def test_deduplicate_removes_duplicates():
    opps = [
        Opportunity(title="SWE Intern", company="Google", location="Bengaluru"),
        Opportunity(title="SWE Intern", company="Google", location="Bengaluru"),
        Opportunity(title="Data Analyst", company="Flipkart", location="Mumbai"),
    ]
    result, removed = deduplicate(opps)
    assert len(result) == 2
    assert removed == 1


def test_deduplicate_keeps_all_unique():
    opps = [
        Opportunity(title="SWE Intern", company="Google", location="Bengaluru"),
        Opportunity(title="Data Scientist", company="Amazon", location="Hyderabad"),
        Opportunity(title="Frontend Dev", company="Razorpay", location="Bengaluru"),
    ]
    result, removed = deduplicate(opps)
    assert len(result) == 3
    assert removed == 0


def test_deduplicate_empty_list():
    result, removed = deduplicate([])
    assert result == []
    assert removed == 0
