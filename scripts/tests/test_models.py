"""Tests for core data models."""

from datetime import date, timedelta

from scripts.core.models import Category, Opportunity


def test_opportunity_fingerprint_is_stable():
    o1 = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    o2 = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    assert o1.id == o2.id


def test_opportunity_fingerprint_differs_on_change():
    o1 = Opportunity(title="SWE Intern", company="Google", location="Bengaluru")
    o2 = Opportunity(title="SWE Intern", company="Microsoft", location="Bengaluru")
    assert o1.id != o2.id


def test_opportunity_to_dict_round_trip():
    opp = Opportunity(
        title="Backend Intern",
        company="Flipkart",
        category="internship",
        apply_link="https://example.com",
        location="Bengaluru, India",
    )
    d = opp.to_dict()
    restored = Opportunity.from_dict(d)
    assert restored.title == opp.title
    assert restored.company == opp.company
    assert restored.id == opp.id


def test_opportunity_is_expired_past_deadline():
    past = (date.today() - timedelta(days=5)).isoformat()
    opp = Opportunity(title="Old Job", company="X", deadline=past)
    assert opp.is_expired() is True


def test_opportunity_is_not_expired_future_deadline():
    future = (date.today() + timedelta(days=30)).isoformat()
    opp = Opportunity(title="New Job", company="X", deadline=future)
    assert opp.is_expired() is False


def test_opportunity_no_deadline_not_expired():
    opp = Opportunity(title="No Deadline", company="X")
    assert opp.is_expired() is False


def test_category_enum_values():
    assert Category.INTERNSHIP.value == "internship"
    assert Category.HACKATHON.value == "hackathon"


def test_opportunity_default_date_set():
    opp = Opportunity(title="T", company="C")
    assert opp.date_found == date.today().isoformat()
    assert opp.last_checked == date.today().isoformat()
