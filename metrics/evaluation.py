from metrics.test_metric import testMetric, requestResultSparql
from datetime import datetime, timedelta
import time

#########################
class Evaluation():
    start_time = None
    end_time = None

    score = None
    # result_json = None
    result_text = None
    reason = None


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

    def get_current_time(self):
        return datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    def get_score(self):
        return self.score

    def get_reason(self):
        return self.reason

    # def evaluate(self):
    #     self.set_start_time()
    #     self.result_text = testMetric(self.api_url, self.tested_resource)
    #     self.set_end_time()
    #     # self.result_json = json.loads(self.result_text)
    #     self.set_score(requestResultSparql(self.result_text, "ss:SIO_000300"))

    def get_test_time(self):
        return self.end_time - self.start_time

    def __str__(self):
        return "Evaluation started at " + str(self.start_time) + " and ended at " + str(self.end_time)

    def __str__(self):
        return f"FAIR metrics evaluation : " \
               f"\n\t started at {self.start_time} " \
               f"\n\t lasted {self.get_test_time()} " \
               f"\n\t score {self.score} " \
               f"\n\t reason {self.reason} " \
