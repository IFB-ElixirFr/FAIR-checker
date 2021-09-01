import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.Evaluation import Result


class F1BTestCase(unittest.TestCase):
    def test_identifiers(self):
        biotools = "http://bio.tools/bwa"
        res = FAIRMetricsFactory.get_F1B(url=biotools).evaluate()
        print(res)
        self.assertEqual(res, Result.NO)

        dataverse = (
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = FAIRMetricsFactory.get_F1B(url=dataverse).evaluate()
        print(res)
        self.assertEqual(res, Result.NO)

        datacite = "https://search.datacite.org/works/10.7892/boris.108387"
        res = FAIRMetricsFactory.get_F1B(url=datacite).evaluate()
        print(res)
        self.assertEqual(res, Result.NO)


if __name__ == "__main__":
    unittest.main()
