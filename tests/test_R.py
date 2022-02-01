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


class ReuseTestCase(unittest.TestCase):
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
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_R11_biotools(self):
        biotools = ReuseTestCase.tool
        res = FAIRMetricsFactory.get_R11(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(
            res.get_score(), str(Result.NO.value)
        )  # TODO to be fixed with Thomas use the Result enum rather than int values

    def test_R12_biotools(self):
        biotools = ReuseTestCase.tool
        res = FAIRMetricsFactory.get_R12(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.NO.value))

    def test_R13_biotools(self):
        biotools = ReuseTestCase.tool
        res = FAIRMetricsFactory.get_R13(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))

    def test_R11_workflowhub(self):
        wf = ReuseTestCase.wf
        res = FAIRMetricsFactory.get_R11(
            web_resource=wf, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.STRONG.value))

    def test_R12_workflowhub(self):
        wf = ReuseTestCase.wf
        res = FAIRMetricsFactory.get_R12(
            web_resource=wf, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.NO.value))

    def test_R13_workflowhub(self):
        wf = ReuseTestCase.wf
        res = FAIRMetricsFactory.get_R13(
            web_resource=wf, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))


if __name__ == "__main__":
    unittest.main()
