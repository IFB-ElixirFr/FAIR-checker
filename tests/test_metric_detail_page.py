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

    def test_returns_turtle_when_accept_turtle(self):
        response = self.client.get("/test/F1A", headers={"Accept": "text/turtle"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/turtle", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="turtle")
        self.assertGreater(len(g), 5)

    def test_returns_jsonld_when_accept_jsonld(self):
        response = self.client.get(
            "/test/F1A", headers={"Accept": "application/ld+json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/ld+json", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="json-ld")
        self.assertGreater(len(g), 5)

    def test_returns_rdfxml_when_accept_rdfxml(self):
        response = self.client.get(
            "/test/F1A", headers={"Accept": "application/rdf+xml"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/rdf+xml", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="xml")
        self.assertGreater(len(g), 5)

    def test_returns_turtle_via_format_param(self):
        response = self.client.get("/test/F1A?format=turtle")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/turtle", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="turtle")
        self.assertGreater(len(g), 5)

    def test_returns_turtle_via_format_param(self):
        response = self.client.get("/test/F1A?format=json-ld")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/ld+json", response.content_type)
        g = ConjunctiveGraph()
        g.parse(data=response.data, format="json-ld")
        self.assertGreater(len(g), 5)

    def test_returns_html_by_default(self):
        response = self.client.get("/test/F1A")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)


if __name__ == "__main__":
    unittest.main()
