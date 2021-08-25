import unittest
from metrics.R_1_1_Impl import R_1_1_Impl


class TestingLicenses(unittest.TestCase):
    uri = "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
    metric = R_1_1_Impl("https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX")

    def test_get(self):
        metric = self.metric
        print(metric.get_api())
        print(metric.is_valid_uri(self.uri))
        metric.evaluate()

    def test_extract_html_selenium(self):
        metric = self.metric
        metric.extract_html_selenium()
        # check that html_source is actually html
        metric.get_html_source()
        metric.extract_rdf()
        graph = metric.get_jsonld()
        print(len(graph))
        self.assertGreater(len(graph), 0)

    def test_extract_html_requests(self):
        metric = self.metric
        metric.extract_html_requests()
        # check that html_source is actually html
        metric.get_html_source()
        metric.extract_rdf()
        graph = metric.get_jsonld()
        print(len(graph))
        self.assertGreater(len(graph), 0)



    def test_license_workflowhub_weak(self):
        metric = R_1_1_Impl("https://workflowhub.eu/workflows/45")
        res = metric.weak_evaluate()
        self.assertEqual(True, res)

    def test_license_dataverse_strong(self):
        metric = R_1_1_Impl(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = metric.weak_evaluate()
        self.assertEqual(False, res)

    def test_license_workflowhub_strong(self):
        metric = R_1_1_Impl("https://workflowhub.eu/workflows/45")
        res = metric.strong_evaluate()
        self.assertEqual(True, res)

    def test_license_dataverse_strong(self):
        metric = R_1_1_Impl(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = metric.strong_evaluate()
        self.assertEqual(False, res)


if __name__ == "__main__":
    unittest.main()
