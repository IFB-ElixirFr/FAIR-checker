import sys
from metrics.Evaluation import Evaluation

sys.path.insert(1, "..")

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.test_metric import getMetrics

# from metrics.evaluation import Evaluation
from pymongo import MongoClient
from datetime import datetime, date, timedelta

import metrics.statistics as stats

import unittest


# @unittest.skip("to be run through a cron and with a specific test DB")
class StatisticsTestCase(unittest.TestCase):
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
                principle = metric["principle"].rsplit("/", 1)[-1]
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

    def test_number_eva(self):
        client = MongoClient()
        db = client.fair_checker
        evaluations = db.evaluations
        all_eval = evaluations.count_documents({})
        print(f"{all_eval} stored evaluation")

        unique_eval = evaluations.distinct("target_uri")
        print(unique_eval)

        six_month_ago = datetime.now() - timedelta(180)
        print(six_month_ago.isoformat())
        print(datetime.now().isoformat())
        sixm_eval = evaluations.count_documents({"started_at": {"$gt": six_month_ago}})
        print(sixm_eval)

    def test_basic_stats(self):
        client = MongoClient()
        db = client.fair_checker
        db_eval = db.evaluations
        n1 = db_eval.count_documents({})
        print(f"{n1} stored evaluation")
        result = self.metrics[0].evaluate("http://bio.tools/bwa")
        n2 = db_eval.count_documents({})
        print(f"{n2} stored evaluation")
        self.assertEqual(n2, n1 + 1)

    def test_count_this_week(self):
        client = MongoClient()
        db = client.fair_checker
        evaluations = db.evaluations

        a_day_ago = datetime.now() - timedelta(1)
        a_week_ago = datetime.now() - timedelta(7)
        a_month_ago = datetime.now() - timedelta(30)

        # nb_eval = evaluations.find({"started_at": {"$gt": a_day_ago}}).count_documents()
        nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}})
        print(nb_eval)

    def test_count_success_this_week(self):
        client = MongoClient()
        db = client.fair_checker
        evaluations = db.evaluations

        a_day_ago = datetime.now() - timedelta(1)
        a_week_ago = datetime.now() - timedelta(7)
        a_month_ago = datetime.now() - timedelta(30)

        nb_eval = evaluations.count_documents(
            {"started_at": {"$gt": a_week_ago}, "success": "1"}
        )
        print(nb_eval)

    def test_count_failed_this_week(self):
        client = MongoClient()
        db = client.fair_checker
        evaluations = db.evaluations

        a_day_ago = datetime.now() - timedelta(1)
        a_week_ago = datetime.now() - timedelta(7)
        a_month_ago = datetime.now() - timedelta(30)

        nb_eval = evaluations.count_documents(
            {"started_at": {"$gt": a_week_ago}, "success": "0"}
        )
        print(nb_eval)

    def test_per_principle(self):
        print(stats.this_week_for_named_metrics(prefix="F", success=1))
        print(stats.this_week_for_named_metrics(prefix="F", success=0))

    def test_record_eval(self):
        e = Evaluation()
        print(e)
        e.persist(source="http://test")


if __name__ == "__main__":
    unittest.main()
