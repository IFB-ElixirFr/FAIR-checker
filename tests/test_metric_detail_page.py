import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_metric_detail_page_returns_200_for_valid_tag(client):
    response = client.get("/test/F1A")
    assert response.status_code == 200


def test_metric_detail_page_case_insensitive(client):
    response = client.get("/test/f1a")
    assert response.status_code == 200


def test_metric_detail_page_returns_404_for_unknown_tag(client):
    response = client.get("/test/ZZZZ")
    assert response.status_code == 404


def test_metric_detail_page_contains_tag(client):
    response = client.get("/test/F1A")
    assert b"F1A" in response.data


def test_metric_detail_page_contains_principle_link(client):
    response = client.get("/test/F1A")
    assert b"https://w3id.org/fair/principles/terms/F1" in response.data
