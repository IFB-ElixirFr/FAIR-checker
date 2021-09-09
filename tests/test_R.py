import logging
import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.FAIRMetricsFactory import Implem
from metrics.Evaluation import Result
from metrics.WebResource import WebResource


class ReuseTestCase(unittest.TestCase):
    def test_R11_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_R11(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)

    def test_R12_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_R12(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.NO)

    def test_R13_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_R13(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.WEAK)


if __name__ == "__main__":
    unittest.main()
