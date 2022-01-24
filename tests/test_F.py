import logging
import unittest
import sys

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.FAIRMetricsFactory import Implem
from metrics.Evaluation import Result
from metrics.WebResource import WebResource

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger()
if not LOGGER.handlers:
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))


class FindabilityTestCase(unittest.TestCase):

    uri_wf = "https://workflowhub.eu/workflows/45"
    uri_tool = "https://bio.tools/bwa"
    wf = None
    tool = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tool = WebResource(cls.uri_tool)
        cls.wf = WebResource(cls.uri_wf)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_F1A_biotools_none(self):
        metric_f1a = FAIRMetricsFactory.get_F1A(impl=Implem.FAIR_CHECKER)
        web_resource = WebResource("https://bio.tools/bwa")
        metric_f1a.set_web_resource(web_resource)
        print(metric_f1a)
        res = metric_f1a.evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))

    def test_F1A_biotools(self):
        biotools = FindabilityTestCase.tool
        res = FAIRMetricsFactory.get_F1A(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))

    def test_cached_F2B_biotools(self):
        biotools = FindabilityTestCase.tool

        res4 = FAIRMetricsFactory.get_R11(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res4)
        self.assertEqual(res4.get_score(), str(Result.NO.value))

        res1 = FAIRMetricsFactory.get_F2B(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res1)
        self.assertEqual(res1.get_score(), str(Result.WEAK.value))

        res2 = FAIRMetricsFactory.get_F2B(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res2)
        self.assertEqual(res2.get_score(), str(Result.WEAK.value))

        res3 = FAIRMetricsFactory.get_I2(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res3)
        self.assertEqual(res3.get_score(), str(Result.WEAK.value))

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
        self.assertEqual(res.get_score(), str(Result.STRONG.value))

    def test_F1B_biotools(self):
        biotools = FindabilityTestCase.tool
        res = FAIRMetricsFactory.get_F1B(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.STRONG.value))

    def test_F2A_biotools(self):
        biotools = FindabilityTestCase.tool
        res = FAIRMetricsFactory.get_F2A(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.STRONG.value))

    def test_F2B_biotools(self):
        biotools = FindabilityTestCase.tool
        res = FAIRMetricsFactory.get_F2B(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))

    def test_identifiers_dataverse(self):
        dataverse = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = FAIRMetricsFactory.get_F1B(web_resource=dataverse).evaluate()
        print(res)
        self.assertEqual(res.get_score(), str(Result.NO.value))

    def test_identifiers_datacite(self):
        datacite = WebResource("https://search.datacite.org/works/10.7892/boris.108387")
        res = FAIRMetricsFactory.get_F1B(web_resource=datacite).evaluate()
        print(res)
        self.assertEqual(res.get_score(), str(Result.NO.value))


if __name__ == "__main__":
    unittest.main()
