from datetime import datetime, timedelta
from pymongo import MongoClient
from enum import Enum, unique
import logging
from io import StringIO
import uuid


@unique
class Result(Enum):
    NO = 0
    WEAK = 1
    STRONG = 2

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.name


#########################
class Evaluation:
    eval_logger = None
    log_capture_string = None

    start_time = None
    end_time = None
    score = None
    recommendation = "No recommendation, metric validated"

    # Result_tet and reason are used by FAIRMetrics only (result_text: whole nanopub content, reason: comment/log)
    result_text = None
    reason = None

    web_resource = None
    metrics = None
    target_uri = None
    implem = None

    # def __init__(self):
    #     pass

    def __init__(self):
        self.log_capture_string = StringIO()
        ### Create the logger
        # self.eval_logger = logging.getLogger("eval_logger")
        logger_id = str(uuid.uuid4())
        self.eval_logger = logging.getLogger(logger_id)
        self.eval_logger.setLevel(logging.DEBUG)
        # self.eval_logger.propagate = False

        ### Setup the console handler with a StringIO object
        console_handler = logging.StreamHandler(self.log_capture_string)
        # console_handler.setLevel(logging.DEBUG)

        ### Add a formatter
        formatter = logging.Formatter(
            "%(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S"
            # "[%(asctime)s] - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        ### Add the console handler to the logger
        self.eval_logger.addHandler(console_handler)

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

    def get_log_html(self):
        return self.log_capture_string.getvalue().replace("\n", "<br>")

    def close_log_stream(self):
        self.log_capture_string.close()

    def set_score(self, score):
        self.score = str(int(float(score)))

    def set_start_time(self):
        self.start_time = self.get_current_time()

    def set_end_time(self):
        self.end_time = self.get_current_time()

    def set_recommendations(self, recommendation_text):
        self.recommendation = recommendation_text

    # used by FAIRMetrics, will probably be replaced by logs
    def set_reason(self, r):
        self.reason = r

    # used by FAIRMetrics, will probably be replaced by logs
    def append_reason(self, r):
        self.reason = self.reason + "\n" + r

    def set_web_resource(self, web_resource):
        self.web_resource = web_resource

    def set_metrics(self, metrics):
        self.metrics = str(metrics)

    def set_target_uri(self, target_uri):
        self.target_uri = str(target_uri)

    def set_implem(self, implem):
        self.implem = implem

    # TODO check https://pymongo.readthedocs.io/en/stable/examples/datetimes.html
    def get_current_time(self):
        # return datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        # return datetime.now().isoformat()
        return datetime.now()

    def get_score(self):
        return self.score

    def get_recommendation(self):
        return self.recommendation

    def get_web_resource(self):
        return self.web_resource

    # used by FAIRMetrics, will probably be replaced by logs
    def get_reason(self):
        return self.reason

    def get_metrics(self):
        return self.metrics

    def get_target_uri(self):
        return self.target_uri

    def get_implem(self):
        return self.implem

    def persist(self):
        client = MongoClient()
        db = client.fair_checker
        db_eval = db.evaluations

        eval = {
            "target_uri": self.target_uri,
            "metrics": self.metrics,
            "implementation": self.implem,
            "started_at": self.start_time,
            "ended_at": self.end_time,
            "success": self.score,
            "reason": self.reason,
            "log": self.log_capture_string.getvalue(),
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
