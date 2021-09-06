import logging
import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.FAIRMetricsFactory import Implem
from metrics.Evaluation import Result
from metrics.WebResource import WebResource


class FindabilityTestCase(unittest.TestCase):
    def test_F1A_biotools_fm_API(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_F1A(
            web_resource=biotools, impl=Implem.FAIR_METRICS_API
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)

    def test_F1A_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_F1A(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)

    def test_F1A_dataverse(self):
        dataverse = WebResource(
            # "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/DOMEHB"
            # "https://data.inrae.fr/api/datasets/export?exporter=schema.org&persistentId=doi%3A10.15454/DOMEHB"
        )
        res = FAIRMetricsFactory.get_F1A(
            web_resource=dataverse, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)

    def test_F1B_biotools_fm_API(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_F1B(
            web_resource=biotools, impl=Implem.FAIR_METRICS_API
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.NO)

    def test_F1B_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_F1B(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.WEAK)

    def test_identifiers_dataverse(self):
        dataverse = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = FAIRMetricsFactory.get_F1B(web_resource=dataverse).evaluate()
        print(res)
        self.assertEqual(res, Result.NO)

    def test_identifiers_datacite(self):
        datacite = WebResource("https://search.datacite.org/works/10.7892/boris.108387")
        res = FAIRMetricsFactory.get_F1B(web_resource=datacite).evaluate()
        print(res)
        self.assertEqual(res, Result.NO)


if __name__ == "__main__":
    unittest.main()
