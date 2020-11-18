from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.test_metric import getMetrics
#from metrics.evaluation import Evaluation

import unittest


class AbstractMetricsTestCase(unittest.TestCase):
    metrics = []
    factory = None

    @classmethod
    def setUpClass(cls) -> None:
        json_metrics = getMetrics()
        factory = FAIRMetricsFactory()

        # for i in range(1,3):
        try:
            # metrics.append(factory.get_metric("test_f1"))
            # metrics.append(factory.get_metric("test_r2"))
            for metric in json_metrics:
                # remove "FAIR Metrics Gen2" from metric name
                name = metric["name"].replace('FAIR Metrics Gen2- ', '')
                # same but other syntax because of typo
                name = name.replace('FAIR Metrics Gen2 - ', '')
                principle = metric["principle"].rsplit('/', 1)[-1]
                cls.metrics.append(factory.get_metric(
                    name,
                    metric["@id"],
                    metric["description"],
                    metric["smarturl"],
                    principle,
                    metric["creator"],
                    metric["created_at"],
                    metric["updated_at"],
                ))
        except ValueError as e:
            print(f"no metrics implemention for {e}")

    def test_bw(self):
        result = self.metrics[2].evaluate("http://bio.tools/bw")
        self.assertEqual(str(0), str(result.get_score()))

    def test_bwa(self):
        result = self.metrics[0].evaluate("http://bio.tools/bwa")
        self.assertEqual(str(1), str(result.get_score()))

if __name__ == '__main__':
    unittest.main()
