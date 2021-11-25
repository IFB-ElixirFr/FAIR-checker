from datetime import datetime, timedelta
from pymongo import MongoClient
from enum import Enum, unique
import logging
from io import StringIO

@unique
class Result(Enum):
    NO = 1
    WEAK = 2
    STRONG = 3

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


#########################
class Evaluation:

    ### Create the logger
    eval_logger = logging.getLogger('eval_logger')
    eval_logger.setLevel(logging.DEBUG)

    ### Setup the console handler with a StringIO object
    log_capture_string = StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)

    ### Add a formatter
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)

    ### Add the console handler to the logger
    eval_logger.addHandler(ch)

    start_time = None
    end_time = None
    score = None
    result_text = None
    reason = None
    metrics = None
    target_uri = None

    def __init__(self):
        pass

    def log_debug(self, message):
        self.eval_logger.debug(message)

    def log_info(self, message):
        self.eval_logger.info(message)

    def log_warning(self, message):
        self.eval_logger.warning(message)

    def log_error(self, message):
        self.eval_logger.error(message)

    def log_critical(self, message):
        self.eval_logger.critical(message)

    def get_log(self):
        return self.log_capture_string.getvalue()

    def close_log_stream(self):
        self.log_capture_string.close()

    def set_score(self, score):
        self.score = str(int(float(score)))

    def set_start_time(self):
        self.start_time = self.get_current_time()

    def set_end_time(self):
        self.end_time = self.get_current_time()

    def set_reason(self, r):
        self.reason = r

    def append_reason(self, r):
        self.reason = self.reason + "\n" + r

    def set_metrics(self, metrics):
        self.metrics = str(metrics)

    def set_target_uri(self, target_uri):
        self.target_uri = str(target_uri)

    # TODO check https://pymongo.readthedocs.io/en/stable/examples/datetimes.html
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
            "target_uri": self.target_uri,
            "metrics": self.metrics,
            "started_at": self.start_time,
            "ended_at": self.end_time,
            "success": self.score,
            "reason": self.reason,
        }

        r = db_eval.insert_one(eval)
        return r

    def get_test_time(self):
        return self.end_time - self.start_time

    def __str__(self):
        return (
            f"FAIR metrics evaluation : "
            f"\n\t started at {self.start_time} "
            f"\n\t ended {self.end_time} "
            f"\n\t score {self.score} "
            f"\n\t reason {self.reason} "
        )
