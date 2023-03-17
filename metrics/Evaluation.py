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
    """
    The classe that represent an evaluation, can usef a WebResource and store all de evaluations results and metadata.

    Attributes:
        eval_logger (logging): The logger used to manage the logs of the evaluation
        log_capture_string (StringIO): The variable containing the log stream
        start_time (datetime): Store the starttime of the evaluation
        end_time (datetime): Store the endtime of the evaluation
        score (str): The score of the evaluation, can be 0, 1 or 2
        recommendation (str): The recommendation for the user
        result_text (str): The whole result of the nanopub returne by FAIRMetrics API
        reason (str): The execution log of the FAIRMetrics evaluationr
        web_resource (WebResource): The evaluated WebResource object
        metrics (str): The tag of the metric used to evaluate the WebResource
        target_uri (str): The URI/URL of the evaluated resource
        implem (str): The name of the implementor of the metric

    """

    eval_logger = None
    log_capture_string = None

    start_time = None
    end_time = None
    score = None
    recommendation = "No recommendation, metric validated"

    # Result_text and reason are used by FAIRMetrics only (result_text: whole nanopub content, reason: comment/log)
    # Might be deprecated
    result_text = None
    reason = None

    web_resource = None
    metrics = None
    target_uri = None
    implem = None

    def __init__(self):
        """
        The constructor, instantiate the logger that stores the executions logs in a variable that can be passed to the UI
        """
        self.log_capture_string = StringIO()
        ### Create the logger
        logger_id = str(uuid.uuid4())
        self.eval_logger = logging.getLogger(logger_id)
        self.eval_logger.setLevel(logging.INFO)

        ### Setup the console handler with a StringIO object
        console_handler = logging.StreamHandler(self.log_capture_string)
        # console_handler.setLevel(logging.DEBUG)

        ### Add a formatter
        formatter = logging.Formatter(
            "%(levelname)s - %(message)s",
        )
        console_handler.setFormatter(formatter)

        ### Add the console handler to the logger
        self.eval_logger.addHandler(console_handler)
        self.eval_logger.propagate = False

    def log_debug(self, message):
        """
        Add a debug message to the eval_logger

        Args:
            message (str): The text to add to the logger as debug
        """
        self.eval_logger.debug(message)

    def log_info(self, message):
        """
        Add an info message to the eval_logger

        Args:
            message (str): The text to add to the logger as info
        """
        self.eval_logger.info(message)

    def log_warning(self, message):
        """
        Add a warning message to the eval_logger

        Args:
            message (str): The text to add to the logger as warning
        """
        self.eval_logger.warning(message)

    def log_error(self, message):
        """
        Add an error message to the eval_logger

        Args:
            message (str): The text to add to the logger as error
        """
        self.eval_logger.error(message)

    def log_critical(self, message):
        """
        Add a critical message to the eval_logger

        Args:
            message (str): The text to add to the logger as critical
        """
        self.eval_logger.critical(message)

    def close_log_stream(self):
        """
        Close the string stream of the logger
        """
        self.log_capture_string.close()

    def set_score(self, score):
        """
        Set the resulting score of the evaluation

        Args:
            score (str): A number representif the evaluation score. Usually 0 (failed), 1 (weak), 2 (strong)
        """
        self.score = str(int(float(score)))

    def set_start_time(self):
        """
        Set the start time of the evaluation
        """
        self.start_time = self.get_current_time()

    def set_end_time(self):
        """
        Set the end time of the evaluation
        """
        self.end_time = self.get_current_time()

    def set_recommendations(self, recommendation_text):
        """
        Set the recommendations depending on the evaluation result to help the user improve its score

        Args:
            recommendation_text (str): The text of the recommendation
        """
        self.recommendation = recommendation_text

    # used by FAIRMetrics, need to be replaced by logs
    def set_reason(self, r):
        self.reason = r

    # used by FAIRMetrics, need to be replaced by logs
    def append_reason(self, r):
        self.reason = self.reason + "\n" + r

    def set_web_resource(self, web_resource):
        """
        Set the web resource instance, contains the RDF metadata collected from the resource URL

        Args:
            web_resource (WebResource): The WebResource object instance that will be used for the evaluation
        """
        self.web_resource = web_resource

    def set_metrics(self, metrics):
        """
        Set the TAG of the metric that will be used to evaluate the WebResource

        Args:
            metrics (str): The TAG of the metruc use to evaluate the WebResource
        """
        self.metrics = str(metrics)

    def set_target_uri(self, target_uri):
        """
        Set the URI that is behind evaluated, available in the WebResource object

        Args:
            target_uri (str): The resource URI/URL
        """
        self.target_uri = str(target_uri)

    def set_implem(self, implem):
        """
        Set the implementator of the metric, at the moment it is FAIR-Checker, or FAIRMetrics

        Args:
            implem (str): The name of the implementator of the metric
        """
        self.implem = implem

    def get_log(self):
        """
        Get all the string content stored in the logger

        Returns:
            str: The full log of the evaluation
        """
        return self.log_capture_string.getvalue()

    def get_log_html(self):
        """
        Get all the string content stored in the logger and making it html compatible

        Returns:
            str: The full log of the evaluation
        """
        return self.log_capture_string.getvalue().replace("\n", "<br>")

    # TODO check https://pymongo.readthedocs.io/en/stable/examples/datetimes.html
    def get_current_time(self):
        """
        Get the current time

        Returns:
            datetime: Datetime object
        """
        # return datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        # return datetime.now().isoformat()
        return datetime.now()

    def get_score(self):
        """
        Get the score of the evaluation, can be 0 (failed), 1 (weak success), 2 (strong success)

        Returns:
            str: The score of the evaluation
        """
        return self.score

    def get_recommendation(self):
        """
        Get the recommandation to give to the user to improve its resource

        Returns:
            str: The recommandation for the resource tester
        """
        return self.recommendation

    def get_web_resource(self):
        """
        Get the WebResource instance of the evaluation previously set

        Returns:
            WebResource: WebResource object instance
        """
        return self.web_resource

    # used by FAIRMetrics, need to be replaced by logs
    def get_reason(self):
        """
        The logs of a FAIRMetrics (Mark D W) evaluation returned by its API

        Returns:
            str: The logs of FAIRMetrics evaluation
        """
        return self.reason

    def get_metrics(self):
        """
        Get the tag of the metric that evaluate the WebResource

        Returns:
            str: The tag of the metric evaluating the resource
        """
        return self.metrics

    def get_target_uri(self):
        """
        Get the URI/URL of the resource being evaluated

        Returns:
            str: The URI/URL of the resource
        """
        return self.target_uri

    def get_implem(self):
        """
        Get the implementator of the metric, at the moment it is FAIR-Checker, or FAIRMetrics

        Returns:
            str: The name of the implementator of the metric
        """
        return self.implem

    def get_test_time(self):
        """
        Get the test time delta of the evaluation between start and end

        Returns:
            datetime: The time lenght of the evaluation
        """
        return self.end_time - self.start_time

    def persist(self, source="UI"):
        """
        Persist in a mongoDB database the resulte of the evaluation, the persisted evaluation has the information if it is executed from the UI or the API

        Args:
            source (str, optional): _description_. Defaults to "UI".

        Returns:
            _type_: _description_
        """
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
            "source": source,
        }

        r = db_eval.insert_one(eval)
        return r

    def __str__(self):
        """
        The string returner to describe the Evaluation instance

        Returns:
            str: The content of the description of the Evaluation
        """
        return (
            f"FAIR metrics evaluation : "
            f"\n\t started at {self.start_time} "
            f"\n\t ended {self.end_time} "
            f"\n\t score {self.score} "
            f"\n\t reason {self.reason} "
        )
