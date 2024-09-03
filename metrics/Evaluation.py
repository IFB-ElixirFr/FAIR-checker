from datetime import datetime, timedelta
from pymongo import MongoClient
from enum import Enum, unique
import logging
from io import StringIO
import uuid
from string import Template

prefix = """
@prefix daq: <http://purl.org/eis/vocab/daq#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix duv: <http://www.w3.org/ns/duv#> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

@prefix : <https://fair-checker.france-bioinformatique.fr/data/> .
"""

FC_spec = [
    {"id": "F1A", "category": "Findable", "label": "Unique IDs", "definition": ""},
    {"id": "F1B", "category": "Findable", "label": "Persistent IDs", "definition": ""},
    {
        "id": "F2A",
        "category": "Findable",
        "label": "Structured metadata",
        "definition": "",
    },
    {
        "id": "F2B",
        "category": "Findable",
        "label": "Shared vocabularies for metadata",
        "definition": "",
    },
    {
        "id": "A1.1",
        "category": "Accessible",
        "label": "Open resolution protocol",
        "definition": "",
    },
    {
        "id": "A1.2",
        "category": "Accessible",
        "label": "Authorisation procedure or access rights",
        "definition": "",
    },
    {
        "id": "I1",
        "category": "Interoperable",
        "label": "Machine readable format",
        "definition": "",
    },
    {
        "id": "I2",
        "category": "Interoperable",
        "label": "Use shared ontologies",
        "definition": "",
    },
    {
        "id": "I3",
        "category": "Interoperable",
        "label": "External links",
        "definition": "",
    },
    {
        "id": "R1.1",
        "category": "Reusable",
        "label": "Metadata includes license",
        "definition": "",
    },
    {
        "id": "R1.2",
        "category": "Reusable",
        "label": "Metadata includes provenance",
        "definition": "",
    },
    {
        "id": "R1.3",
        "category": "Reusable",
        "label": "Community standards",
        "definition": "",
    },
]


FAIR_Checker_template = """
:$metric_id
    a dqv:Dimension ;
    skos:prefLabel "$metric_label"@en ;
    skos:definition "$metric_definition"@en ;
    dqv:inCategory :$category ."""

metrics_tpl = """
:$id
    a dqv:QualityMeasurement ;
    dqv:computedOn <$url> ;
    dqv:isMeasurementOf :$dimension ;
    dqv:value "$value"^^xsd:integer ;
    prov:generatedAtTime "$date"^^xsd:dateTime ;
    prov:wasAttributedTo <https://github.com/IFB-ElixirFr/fair-checker> ;
    rdfs:seeAlso <https://doi.org/10.1186/s13326-023-00289-5> ."""


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

    _id = None
    web_resource = None
    metrics = None
    target_uri = None
    implem = None

    # def __init__(self):
    #     pass

    def __init__(self):
        self.log_capture_string = StringIO()
        # Create the logger
        # self.eval_logger = logging.getLogger("eval_logger")
        logger_id = str(uuid.uuid4())
        self.eval_logger = logging.getLogger(logger_id)
        self.eval_logger.setLevel(logging.INFO)
        # self.eval_logger.propagate = False

        # Setup the console handler with a StringIO object
        console_handler = logging.StreamHandler(self.log_capture_string)
        # console_handler.setLevel(logging.DEBUG)

        # Add a formatter
        formatter = logging.Formatter(
            "%(levelname)s - %(message)s",
            # "%Y-%m-%d %H:%M:%S"
            # "[%(asctime)s] - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.eval_logger.addHandler(console_handler)
        self.eval_logger.propagate = False

    def build_from_json(self, data):
        self.__init__()
        if "_id" in data.keys():
            self._id = data["_id"]
        if "target_uri" in data.keys():
            self.set_target_uri(data["target_uri"])
        if "implementation" in data.keys():
            self.set_implem(data["implementation"])
        if "success" in data.keys():
            self.set_score(data["success"])
        if "reason" in data.keys():
            self.set_reason(data["reason"])
        if "metrics" in data.keys():
            self.set_metrics(data["metrics"])
        if "started_at" in data.keys():
            self.start_time = data["started_at"]
        if "ended_at" in data.keys():
            self.end_time = data["ended_at"]
        if "log" in data.keys():
            self.set_recommendations(data["log"])

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

    def set_recommendations(self, recommendation_text: str):
        self.recommendation = recommendation_text

    # used by FAIRMetrics, will probably be replaced by logs
    def set_reason(self, r: str):
        self.reason = r

    # used by FAIRMetrics, will probably be replaced by logs
    def append_reason(self, r: str):
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

    def persist(self, source="UI"):
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

    def get_test_time(self):
        return self.end_time - self.start_time

    def to_rdf_turtle(self, id):

        d = None
        eval_ttl = ""
        spec_ttl = ""

        if not self._id:
            self._id = id

        if self.end_time:
            d = self.end_time.isoformat()

        if self.score:
            eval_ttl = Template(metrics_tpl).safe_substitute(
                id=str(self._id),
                url=self.get_target_uri().strip(),
                dimension=self.get_metrics(),
                value=self.get_score(),
                date=d,
            )
        ttl = prefix + eval_ttl

        for spec in FC_spec:
            if self.get_metrics() == spec["id"]:
                spec_ttl = Template(FAIR_Checker_template).safe_substitute(
                    metric_id=spec["id"],
                    metric_label=spec["label"],
                    metric_definition=spec["definition"],
                    category=spec["category"],
                )
                ttl += spec_ttl

        return ttl

    def __str__(self):
        return (
            f"FAIR metrics evaluation : "
            f"\n\t started at {self.start_time} "
            f"\n\t ended {self.end_time} "
            f"\n\t score {self.score} "
            f"\n\t reason {self.reason} "
        )
