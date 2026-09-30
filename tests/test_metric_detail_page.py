import unittest

from app import app


class MetricDetailPageTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_metric_detail_page_returns_200_for_valid_tag(self):
        response = self.client.get("/test/F1A")
        self.assertEqual(response.status_code, 200)

    def test_metric_detail_page_case_insensitive(self):
        response = self.client.get("/test/f1a")
        self.assertEqual(response.status_code, 200)

    def test_metric_detail_page_returns_404_for_unknown_tag(self):
        response = self.client.get("/test/ZZZZ")
        self.assertEqual(response.status_code, 404)

    def test_metric_detail_page_contains_tag(self):
        response = self.client.get("/test/F1A")
        self.assertIn(b"F1A", response.data)

    def test_metric_detail_page_contains_principle_link(self):
        response = self.client.get("/test/F1A")
        self.assertIn(b"https://w3id.org/fair/principles/terms/F1", response.data)


if __name__ == "__main__":
    unittest.main()
