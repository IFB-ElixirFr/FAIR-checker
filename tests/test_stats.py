import sys
from metrics.Evaluation import Evaluation
from metrics.util import gen_usage_statistics
from metrics.statistics import (
    validation_this_month,
    validation_this_month_v2,
    md_harvesting_this_month,
)

sys.path.insert(1, "..")

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.test_metric import getMetrics

# from metrics.evaluation import Evaluation
from pymongo import MongoClient
from datetime import datetime, date, timedelta
import metrics.statistics as stats
import unittest
import json


# @unittest.skip("to be run through a cron and with a specific test DB")
class StatisticsTestCase(unittest.TestCase):
    # metrics = []
    # factory = None
    # @classmethod
    # def setUpClass(cls) -> None:

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
        print(stats.this_month_for_named_metrics(prefix="F", success=1))
        print(stats.this_month_for_named_metrics(prefix="F", success=0))

    def test_gen_stat_file(self):
        gen_usage_statistics()
        with open("../data/usage_stats.json", "r") as infile:
            usage_stats = json.load(infile)
            self.assertGreaterEqual(usage_stats["evals_30"], 0)

    def test_record_eval(self):
        e = Evaluation()
        print(e)
        e.persist(source="http://test")

    def test_nb_valid(self):
        print(f"{md_harvesting_this_month()} metadata harvesting this month")
        print(f"{validation_this_month()} valid this month")
        print(f"{validation_this_month_v2()} valid broad this month")


if __name__ == "__main__":
    unittest.main()
