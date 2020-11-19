from metrics.test_metric import testMetric, requestResultSparql
from datetime import datetime, timedelta
import time
import json
from pymongo import MongoClient

#########################
class Evaluation():
    start_time = None
    end_time = None
    score = None
    result_text = None
    reason = None
    metrics = None
    target_uri = None

    def __init__(self):
        pass

    def set_score(self, score):
        self.score = str(int(float(score)))

    def set_start_time(self):
        self.start_time = self.get_current_time()

    def set_end_time(self):
        self.end_time = self.get_current_time()

    def set_reason(self, r):
        self.reason = r

    def set_metrics(self, metrics):
        self.metrics = str(metrics)

    def set_target_uri(self, target_uri):
        self.target_uri = str(target_uri)

    #TODO check https://pymongo.readthedocs.io/en/stable/examples/datetimes.html
    def get_current_time(self):
        # return datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        # return datetime.now().isoformat()
        return datetime.now()

    def get_score(self):
        return self.score

    def get_reason(self):
        return self.reason

    def get_metrics(self):
        return self.metrics

    def get_target_uri(self):
        return self.target_uri

    def persist(self):
        client = MongoClient()
        db = client.fair_checker
        db_eval = db.evaluations

        eval = {
            'target_uri': self.target_uri,
            'metrics': self.metrics,
            'started_at': self.start_time,
            'ended_at': self.end_time,
            'success': self.score,
            'reason': self.reason
        }

        r = db_eval.insert_one(eval)
        return r

    def get_test_time(self):
        return self.end_time - self.start_time

    def __str__(self):
        return f"FAIR metrics evaluation : " \
               f"\n\t started at {self.start_time} " \
               f"\n\t lasted {self.get_test_time()} " \
               f"\n\t score {self.score} " \
               f"\n\t reason {self.reason} " \
