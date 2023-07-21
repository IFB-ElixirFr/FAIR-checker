import logging
from time import sleep
import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.FAIRMetricsFactory import Implem
from metrics.Evaluation import Result
from metrics.WebResource import WebResource


class InteroperablilityTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    # def tearDown(self) -> None:
    #     sleep(1)
    #     return super().tearDown()

    def test_I1_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I1(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.WEAK.value))

    @unittest.skip("Deprecated metrics")
    def test_I2A_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I2A(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.NO.value))

    def test_I3_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I3(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res.get_score(), str(Result.STRONG.value))


if __name__ == "__main__":
    unittest.main()
