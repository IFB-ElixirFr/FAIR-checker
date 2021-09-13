import logging
import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.FAIRMetricsFactory import Implem
from metrics.Evaluation import Result
from metrics.WebResource import WebResource


class InteroperablilityTestCase(unittest.TestCase):
    def test_I1_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I1(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)

    def test_I2A_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I2A(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.NO)

    def test_I3_biotools(self):
        biotools = WebResource("http://bio.tools/bwa")
        res = FAIRMetricsFactory.get_I3(
            web_resource=biotools, impl=Implem.FAIR_CHECKER
        ).evaluate()
        logging.info(res)
        self.assertEqual(res, Result.STRONG)


if __name__ == "__main__":
    unittest.main()
