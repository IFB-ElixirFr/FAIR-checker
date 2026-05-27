import sys
import os
import unittest

from rdflib import ConjunctiveGraph

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


class MetricDetailPageTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    # --- HTML rendering ---

    def test_returns_200_for_valid_tag(self):
        response = self.client.get("/test/F1A")
        self.assertEqual(response.status_code, 200)

    def test_case_insensitive(self):
        response = self.client.get("/test/f1a")
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_unknown_tag(self):
        response = self.client.get("/test/ZZZZ")
        self.assertEqual(response.status_code, 404)

    def test_html_contains_tag(self):
        response = self.client.get("/test/F1A")
        self.assertIn(b"F1A", response.data)

    def test_html_contains_principle_link(self):
        response = self.client.get("/test/F1A")
        self.assertIn(b"https://w3id.org/fair/principles/terms/F1", response.data)

    # --- Content negotiation ---

    def test_returns_turtle_when_accept_turtle(self):
        response = self.client.get("/test/F1A", headers={"Accept": "text/turtle"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/turtle", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="turtle")
        self.assertGreater(len(g), 0)

    def test_returns_jsonld_when_accept_jsonld(self):
        response = self.client.get(
            "/test/F1A", headers={"Accept": "application/ld+json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/ld+json", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="json-ld")
        self.assertGreater(len(g), 0)

    def test_returns_rdfxml_when_accept_rdfxml(self):
        response = self.client.get(
            "/test/F1A", headers={"Accept": "application/rdf+xml"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/rdf+xml", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="xml")
        self.assertGreater(len(g), 0)

    def test_returns_turtle_via_format_param(self):
        response = self.client.get("/test/F1A?format=turtle")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/turtle", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="turtle")
        self.assertGreater(len(g), 0)

    def test_returns_html_by_default(self):
        response = self.client.get("/test/F1A")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)


if __name__ == "__main__":
    unittest.main()
