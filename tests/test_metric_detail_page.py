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


def test_metric_detail_returns_turtle_when_accept_turtle(client):
    response = client.get("/test/F1A", headers={"Accept": "text/turtle"})
    assert response.status_code == 200
    assert "text/turtle" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="turtle")
    assert len(g) > 0


def test_metric_detail_returns_jsonld_when_accept_jsonld(client):
    response = client.get(
        "/test/F1A", headers={"Accept": "application/ld+json"}
    )
    assert response.status_code == 200
    assert "application/ld+json" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="json-ld")
    assert len(g) > 0


def test_metric_detail_returns_rdfxml_when_accept_rdfxml(client):
    response = client.get(
        "/test/F1A", headers={"Accept": "application/rdf+xml"}
    )
    assert response.status_code == 200
    assert "application/rdf+xml" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="xml")
    assert len(g) > 0


def test_metric_detail_returns_turtle_via_format_param(client):
    response = client.get("/test/F1A?format=turtle")
    assert response.status_code == 200
    assert "text/turtle" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="turtle")
    assert len(g) > 0


def test_metric_detail_still_returns_html_by_default(client):
    response = client.get("/test/F1A")
    assert response.status_code == 200
    assert "text/html" in response.content_type
