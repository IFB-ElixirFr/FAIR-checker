import sys

sys.path.insert(1, "..")

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.test_metric import getMetrics

# from metrics.evaluation import Evaluation
from pymongo import MongoClient

import unittest


@unittest.skip("long test, to be run through a cron @GitHub ?")
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
                name = metric["name"].replace("FAIR Metrics Gen2- ", "")
                # same but other syntax because of typo
                name = name.replace("FAIR Metrics Gen2 - ", "")
                principle = metric["principle"]
                cls.metrics.append(
                    factory.get_metric(
                        name,
                        metric["@id"],
                        metric["description"],
                        metric["smarturl"],
                        principle,
                        metric["creator"],
                        metric["created_at"],
                        metric["updated_at"],
                    )
                )
        except ValueError as e:
            print(f"no metrics implemention for {e}")

    @unittest.skip("To be done by a CRON")
    def test_bw(self):
        result = self.metrics[2].evaluate("http://bio.tools/bw")
        self.assertEqual(str(0), str(result.get_score()))

    @unittest.skip("To be done by a CRON")
    def test_bwa(self):
        result = self.metrics[0].evaluate("http://bio.tools/bwa")
        self.assertEqual(str(1), str(result.get_score()))

    @unittest.skip("To be done by a CRON")
    def test_all_bwa(self):
        print("Test all bwa")
        scores = [1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        i = 0
        for m in self.metrics:
            result = m.evaluate("http://bio.tools/bwa")
            self.assertEqual(str(scores[i]), str(result.get_score()))
            i += 1

    @unittest.skip("To be done by a CRON")
    def test_all_pangaea(self):
        print("Test all pangaea")
        scores = [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1]
        i = 0
        for m in self.metrics:

            result = m.evaluate("https://doi.pangaea.de/10.1594/PANGAEA.914331")
            self.assertEqual(str(scores[i]), str(result.get_score()))
            i += 1

    @unittest.skip("To be done by a CRON")
    def test_names(self):
        print("Test all names")
        names = [
            "Unique Identifier",
            "Identifier Persistence",
            "Data Identifier Persistence",
            "Structured Metadata",
            "Grounded Metadata",
            "Data Identifier Explicitly In Metadata",
            "Metadata Identifier Explicitly In Metadata",
            "Searchable in major search engine",
            "Uses open free protocol for data retrieval",
            "Uses open free protocol for metadata retrieval",
            "Data authentication and authorization",
            "Metadata authentication and authorization",
            "Metadata Persistence",
            "Metadata Knowledge Representation Language (weak)",
            "Metadata Knowledge Representation Language (strong)",
            "Data Knowledge Representation Language (weak)",
            "Data Knowledge Representation Language (strong)",
            "Metadata uses FAIR vocabularies (weak)",
            "Metadata uses FAIR vocabularies (strong)",
            "Metadata contains qualified outward references)",
            "Metadata Includes License (strong)",
            "Metadata Includes License (weak)",
        ]
        i = 0
        for m in self.metrics:
            print(m.get_name())
            self.assertEqual(str(names[i]), str(m.get_name()))
            i += 1



if __name__ == "__main__":
    unittest.main()
