import copy
from asyncio.log import logger
import eventlet

# from https://github.com/eventlet/eventlet/issues/670
# eventlet.monkey_patch(select=False)
eventlet.monkey_patch()

import sys
from flask import (
    Flask,
    request,
    render_template,
    send_file,
    send_from_directory,
    make_response,
)
from flask_restx import Resource, Api, fields, reqparse
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_caching import Cache
from os import path
from dotenv import dotenv_values
import secrets
import time
import os
import io
import uuid
import argparse
import functools
from argparse import RawTextHelpFormatter
from datetime import timedelta
import json
from json import JSONDecodeError
from pathlib import Path
import rdflib
from rdflib import ConjunctiveGraph, URIRef
import extruct
import logging
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import track
import metrics.util as util
import metrics.statistics as stats
from metrics import test_metric
from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.WebResource import WebResource
from metrics.Evaluation import Result
from metrics.util import SOURCE
from metrics.F1B_Impl import F1B_Impl
from urllib.parse import urlparse

from profiles.Profile import Profile
from profiles.ProfileFactory import (
    ProfileFactory,
    find_conformsto_subkg,
    load_profiles,
    update_profiles,
    evaluate_profile_with_conformsto,
    evaluate_profile_from_type,
    dyn_evaluate_profile_with_conformsto,
)

import atexit
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
from apscheduler.schedulers.background import BackgroundScheduler

import git

basedir = path.abspath(path.dirname(__file__))

app = Flask(__name__)

app.config.SWAGGER_UI_OPERATION_ID = True
app.config.SWAGGER_UI_REQUEST_DURATION = True


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="FAIR-Checker",
        subtitle="Improve the FAIRness of your web resources",
    )


# app.logger.setLevel(logging.DEBUG)
app.logger.propagate = False

CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

prod_logger = logging.getLogger("PROD")
dev_logger = logging.getLogger("DEV")
app_logger = logging.getLogger("app")
root_logger = logging.getLogger("root")
app_logger.propagate = False
root_logger.propagate = False

# loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
# for logger in loggers:
#     print(logger)

print(f'ENV is set to: {app.config["ENV"]}')

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")

    prod_log_handler = logging.FileHandler("prod.log")
    # prod_log_handler = logging.StreamHandler(sys.stdout)

    ### Add a formatter
    prod_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] %(message)s", "%d/%m/%Y %H:%M:%S"
    )

    prod_log_handler.setFormatter(prod_formatter)
    prod_logger.addHandler(prod_log_handler)

    prod_logger.setLevel(logging.INFO)

    # Prevent DEV logger from output
    dev_logger.propagate = False

    # Update bioschemas profile when starting server in production
    # update_profiles()
else:
    app.config.from_object("config.DevelopmentConfig")

    dev_log_handler = logging.StreamHandler()
    ### Add a formatter
    dev_formatter = logging.Formatter(
        "[%(name)s-%(levelname)s][%(filename)s-%(lineno)d] - %(message)s",
    )

    dev_log_handler.setFormatter(dev_formatter)
    dev_logger.addHandler(dev_log_handler)

    dev_logger.setLevel(logging.DEBUG)

    # Prevent PROD logger from output
    prod_logger.propagate = False

dev_logger.warning("Watch out dev!")
dev_logger.info("I told you so dev")
dev_logger.debug("DEBUG dev")

prod_logger.warning("Watch out prod!")
prod_logger.info("I told you so prod")
prod_logger.debug("DEBUG prod")

# Instanciate the Swagger API
api = Api(
    app=app,
    title="FAIR-Checker API",
    doc="/swagger",
    base_path="https://fair-checker.france-bioinformatique.fr",
    # base_url=app.config["SERVER_IP"],
    description=app.config["SERVER_IP"],
    # url_scheme="https://fair-checker.france-bioinformatique.fr/",
)

metrics_namespace = api.namespace("metrics", description="Metrics assessment")
fc_check_namespace = api.namespace(
    "api/check", description="FAIR Metrics assessment from Check"
)
fc_inspect_namespace = api.namespace(
    "api/inspect", description="FAIR improvement from Inspect"
)

cache = Cache(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

app.secret_key = secrets.token_urlsafe(16)

sample_resources = {
    "Examples": [
        {
            "text": "Dataset Dataverse",
            "url": "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX",
        },
        {
            "text": "Workflow",
            "url": "https://workflowhub.eu/workflows/18",  # Workflow in WorkflowHub
        },
        {
            "text": "Publication Datacite",
            "url": "https://search.datacite.org/works/10.7892/boris.108387",  # Publication in Datacite
        },
        {
            "text": "Dataset",
            "url": "https://doi.pangaea.de/10.1594/PANGAEA.914331",  # dataset in PANGAEA
        },
        {
            "text": "Tool",
            "url": "https://bio.tools/jaspar",
        },
    ],
}

metrics = [
    {"name": "f1", "category": "F", "description": "F1 verifies that ...  "},
    {"name": "f2", "category": "F", "description": "F2 verifies that ...  "},
    {"name": "f3", "category": "F", "description": "F3 verifies that ...  "},
    {"name": "a1", "category": "A"},
    {"name": "a2", "category": "A"},
]

# Load bs profils dict (from github if not already in local)
load_profiles()

METRICS = {}
# json_metrics = test_metric.getMetrics()
factory = FAIRMetricsFactory()

# METRICS_RES = test_metric.getMetrics()
METRICS_CUSTOM = factory.get_FC_metrics()

for i, key in enumerate(METRICS_CUSTOM):
    METRICS_CUSTOM[key].set_id("FC_" + str(i))

KGS = {}

RDF_TYPE = {}

FILE_UUID = ""

DICT_TEMP_RES = {}

STATUS_BIOPORTAL = requests.head("https://bioportal.bioontology.org/").status_code
STATUS_OLS = requests.head("https://www.ebi.ac.uk/ols/index").status_code
STATUS_LOV = requests.head("https://lov.linkeddata.es/dataset/lov/sparql").status_code

DICT_BANNER_INFO = {"banner_message_info": {}}

# Update banner info with the message in .env
@app.context_processor
def display_info():
    """
    Get the message from .env file to display in the UI in a top banner

    Returns:
        dict: Updated dict with the message from the .env
    """
    global DICT_BANNER_INFO

    try:
        env_banner_info = dotenv_values(".env")["BANNER_INFO"]
    except KeyError:
        dev_logger.warning(
            "BANNER_INFO is not set in .env (e.g. BANNER_INFO='Write your message here')"
        )
        DICT_BANNER_INFO["banner_message_info"].pop("env_info", None)
        return DICT_BANNER_INFO

    if env_banner_info != "":
        DICT_BANNER_INFO["banner_message_info"]["env_info"] = env_banner_info
    else:
        DICT_BANNER_INFO["banner_message_info"].pop("env_info", None)

    return DICT_BANNER_INFO


def update_vocab_status():
    """
    Method that check the status_code of BioPortal, OLS and LOV to know if the URLs are UP, if not, dislay it in the info banner
    """
    global DICT_BANNER_INFO, STATUS_BIOPORTAL, STATUS_OLS, STATUS_LOV

    STATUS_BIOPORTAL = requests.head("https://bioportal.bioontology.org/").status_code
    STATUS_OLS = requests.head("https://www.ebi.ac.uk/ols/index").status_code
    STATUS_LOV = requests.head(
        "https://lov.linkeddata.es/dataset/lov/sparql"
    ).status_code

    if STATUS_BIOPORTAL != 200:
        info_bioportal = "BioPortal might not be reachable. Status code: " + str(
            STATUS_BIOPORTAL
        )
        DICT_BANNER_INFO["banner_message_info"]["status_bioportal"] = info_bioportal
    else:
        DICT_BANNER_INFO["banner_message_info"].pop("status_bioportal", None)

    if STATUS_OLS != 200:
        info_ols = "OLS might not be reachable. Status code: " + str(STATUS_OLS)
        DICT_BANNER_INFO["banner_message_info"]["status_ols"] = info_ols
    else:
        DICT_BANNER_INFO["banner_message_info"].pop("status_ols", None)

    if STATUS_LOV != 200:
        info_lov = "LOV might not be reachable. Status code: " + str(STATUS_LOV)
        DICT_BANNER_INFO["banner_message_info"]["status_lov"] = info_lov
    else:
        DICT_BANNER_INFO["banner_message_info"].pop("status_lov", None)

    prod_logger.info("Updating banner status")


@app.context_processor
def display_vocab_status():
    """
    Function that make the banner info dictionnary available for all templates

    Returns:
        dict: Dictionnary containing eventual informations to display in the optional warning banner
    """
    global DICT_BANNER_INFO

    return DICT_BANNER_INFO


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_vocab_status, trigger="interval", seconds=600)
# scheduler.add_job(func=display_info, trigger="interval", seconds=600)
scheduler.add_job(
    func=F1B_Impl.update_identifiers_org_dump, trigger="interval", seconds=604800
)
scheduler.add_job(func=update_profiles, trigger="interval", seconds=604800)

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.context_processor
def inject_app_version():
    """
    Function that make the FAIR-Checker latest version available in all templates using github tags

    Returns:
        dict: Dictionnary containing the latest FAIR-Checker version
    """
    repo = git.Repo(".")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1]
    return dict(version_tag=latest_tag)


@app.context_processor
def inject_jsonld():
    """
    Functione that make the FAIR-Checker JSON-LD available to all templates

    Returns:
        dict: Dictionnary containing the JSON-LD describing FAIR-Checker application
    """
    return dict(jld=buildJSONLD())


@app.route("/favicon.ico")
def favicon():
    """
    Setup FAIR-Checker favicon

    Returns:
        function: Flask function
    """
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/docs/<path:filename>")
def documentation(filename):
    """
    Setup FAIR-Checker user documentation

    Args:
        filename (str): Name of the file that contains the documentation

    Returns:
        function: Flask function to retrieve documentation file
    """
    return send_from_directory("docs/_build/html", filename)


@app.route("/")
def home():
    return render_template(
        # "index.html",
        # title="FAIR-Checker",
        # subtitle="Improve the FAIRness of your web resources",
    )


@app.route("/about")
def about():
    """
    Route to load the about page

    Returns:
        function: Flask template renderer
    """
    return render_template(
        "about.html",
        title="About",
        subtitle="More about FAIR-Checker",
    )


@app.route("/statistics")
def statistics():
    """
    Route to load usage statistics of FAIR-Checker

    Returns:
        function: Flask template renderer
    """
    return render_template(
        "statistics.html",
        title="Statistics",
        subtitle="Visualize usage statistics of FAIR-Checker",
        evals=stats.evaluations_this_week(),
        success=stats.success_this_week(),
        success_weekly=stats.success_weekly_one_year(),
        failures=stats.failures_this_week(),
        failures_weekly=stats.failures_weekly_one_year(),
        f_success_weekly=stats.weekly_named_metrics(prefix="F", success=1),
        f_failures_weekly=stats.weekly_named_metrics(prefix="F", success=0),
        a_success_weekly=stats.weekly_named_metrics(prefix="A", success=1),
        a_failures_weekly=stats.weekly_named_metrics(prefix="A", success=0),
        i_success_weekly=stats.weekly_named_metrics(prefix="I", success=1),
        i_failures_weekly=stats.weekly_named_metrics(prefix="I", success=0),
        r_success_weekly=stats.weekly_named_metrics(prefix="R", success=1),
        r_failures_weekly=stats.weekly_named_metrics(prefix="R", success=0),
        f_success=stats.this_week_for_named_metrics(prefix="F", success=1),
        f_failures=stats.this_week_for_named_metrics(prefix="F", success=0),
        a_success=stats.this_week_for_named_metrics(prefix="A", success=1),
        a_failures=stats.this_week_for_named_metrics(prefix="A", success=0),
        i_success=stats.this_week_for_named_metrics(prefix="I", success=1),
        i_failures=stats.this_week_for_named_metrics(prefix="I", success=0),
        r_success=stats.this_week_for_named_metrics(prefix="R", success=1),
        r_failures=stats.this_week_for_named_metrics(prefix="R", success=0),
    )

# Argument parser for Flask restx API
reqparse = reqparse.RequestParser()
reqparse.add_argument(
    "url",
    type=str,
    required=True,
    location="args",
    help="The URL/DOI of the resource to be evaluated",
)

def generate_check_api(metric):
    """
    Function that automatically generate endpoints to evaluate independently each FAIR-Checker metric

    Args:
        metric (metrics): A metric implementation generated by the FAIRMetricsFactory class
    """
    @fc_check_namespace.route("/metric_" + metric.get_principle_tag())
    class MetricEval(Resource):
        @fc_check_namespace.doc(
            "Evaluate " + metric.get_principle_tag() + " FAIR metric"
        )
        @fc_check_namespace.expect(reqparse)
        def get(self):

            args = reqparse.parse_args()
            url = args["url"]
            web_res = WebResource(url)
            metric.set_web_resource(web_res)
            result = metric.evaluate()
            data = {
                "metric": result.get_metrics(),
                "score": result.get_score(),
                "target_uri": result.get_target_uri(),
                "eval_time": str(result.get_test_time()),
                "recommendation": result.get_recommendation(),
                "comment": result.get_log(),
            }
            result.persist(str(SOURCE.API))
            return data

        get.__doc__ = metric.get_name()

    MetricEval.__name__ = MetricEval.__name__ + metric.get_principle_tag()


for key in METRICS_CUSTOM.keys():
    generate_check_api(METRICS_CUSTOM[key])


@fc_check_namespace.route("/metrics_all")
# @fc_check_namespace.doc(url_fields)
class MetricEvalAll(Resource):

    @fc_check_namespace.doc("Evaluates all FAIR metrics at once")
    @fc_check_namespace.expect(reqparse)
    def get(self):
        """All FAIR metrics"""

        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)

        metrics_collection = []
        for metric_key in METRICS_CUSTOM.keys():
            metric = METRICS_CUSTOM[metric_key]
            metric.set_web_resource(web_res)
            metrics_collection.append(metric)

        # metrics_collection = FAIRMetricsFactory.get_FC_impl(web_res)

        results = []
        for metric in metrics_collection:
            result = metric.evaluate()
            data = {
                "metric": result.get_metrics(),
                "score": result.get_score(),
                "target_uri": result.get_target_uri(),
                "eval_time": str(result.get_test_time()),
                "recommendation": result.get_recommendation(),
                "comment": result.get_log(),
            }
            result.persist(str(SOURCE.API))
            results.append(data)

        return results


# fc_check_namespace.add_resource(MetricEvalAll, "/metrics_all")


@fc_inspect_namespace.route("/get_rdf_metadata")
class RetrieveMetadata(Resource):
    @fc_inspect_namespace.produces(["application/ld+json"])
    @fc_inspect_namespace.expect(reqparse)
    def get(self):
        """Get RDF metadata in JSON-LD from a web resource"""

        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)
        data_str = web_res.get_rdf().serialize(format="json-ld")
        data_json = json.loads(data_str)
        return data_json


describe_list = [
    util.describe_opencitation,
    util.describe_wikidata,
    util.describe_openaire,
]

jsonld_example = '{"@context":"http://schema.org","@type":"ScholarlyArticle","@id":"https://doi.org/10.7892/boris.108387","url":"https://boris.unibe.ch/108387/","name":"Diagnostic value of contrast-enhanced magnetic resonance angiography in large-vessel vasculitis.","author":[{"name":"Sabine Adler","givenName":"Sabine","familyName":"Adler","@type":"Person"},{"name":"Marco Sprecher","givenName":"Marco","familyName":"Sprecher","@type":"Person"},{"name":"Felix Wermelinger","givenName":"Felix","familyName":"Wermelinger","@type":"Person"},{"name":"Thorsten Klink","givenName":"Thorsten","familyName":"Klink","@type":"Person"},{"name":"Harald Marcel Bonel","givenName":"Harald Marcel","familyName":"Bonel","@type":"Person"},{"name":"Peter M Villiger","givenName":"Peter M","familyName":"Villiger","@type":"Person"}],"description":"OBJECTIVE To evaluate contrast-enhanced magnetic resonance angiography (MRA) in diagnosis of inflammatory aortic involvement in patients with clinical suspicion of large-vessel vasculitis. PATIENTS AND METHODS Seventy-five patients, mean age 62 years (range 16-82 years), 44 female and 31 male, underwent gadolinium-enhanced MRA and were evaluated retrospectively. Thoracic MRA was performed in 32 patients, abdominal MRA in 7 patients and both thoracic and abdominal MRA in 36 patients. Temporal arterial biopsies were obtained from 22/75 patients. MRA positivity was defined as increased aortic wall signal in late gadolinium-enhanced axial turbo inversion recovery magnitude (TIRM) series. The influence of prior glucocorticoid intake on MRA outcome was evaluated. RESULTS MRA was positive in 24/75 patients, with lesions located in the thorax in 7 patients, the abdomen in 5 and in both thorax and abdomen in 12. Probability for positive MRA after glucocorticoid intake for more than 5 days before MRA was reduced by 89.3%. Histology was negative in 3/10 MRA-positive patients and positive in 5/12 MRA-negative patients. All 5/12 histology positive / MRA-negative patients had glucocorticoids for &gt;5 days prior to MRA and were diagnosed as having vasculitis. Positive predictive value for MRA was 92%, negative predictive value was 88%. CONCLUSIONS Contrast-enhanced MRA reliably identifies large vessel vasculitis. Vasculitic signals in MRA are very sensitive to glucocorticoids, suggesting that MRA should be done before glucocorticoid treatment.","keywords":"610 Medicine &amp; health","inLanguage":"en","encodingFormat":"application/pdf","datePublished":"2017","schemaVersion":"http://datacite.org/schema/kernel-4","publisher":{"@type":"Organization","name":"EMH Schweizerischer Ärzteverlag"},"provider":{"@type":"Organization","name":"datacite"}}'

""" Model for documenting the API"""
graph_payload = fc_inspect_namespace.model(
    "graph_payload",
    {
        "url": fields.Url(
            description="URL of the resource to be enriched", required=True
        ),
        "json-ld": fields.String(
            description="RDF graph in JSON-LD", required=True, exemple="JSON-LD string"
        ),
    },
)


def generate_ask_api(describe):
    """
    Function that automatically generate endpoints to aggregate RDF metadata from Wikidata, OpenCitations and OpenAIRE

    Args:
        describe (function): A describe function that aggregate metadata from an external endpoint
    """
    @fc_inspect_namespace.route("/" + describe.__name__, methods=["GET"])
    @fc_inspect_namespace.route("/" + describe.__name__ + "/", methods=["POST"])
    # @api.doc(params={"url": "An URL"})
    class Ask(Resource):
        @fc_inspect_namespace.expect(reqparse)
        def get(self):
            """
            The GET method, taking an URL as input

            Returns:
                dict: A dictionnary containing the eventualy aggregated RDF Graph
            """
            args = reqparse.parse_args()
            url = args["url"]

            web_res = WebResource(url)
            kg = web_res.get_rdf()
            old_kg = copy.deepcopy(kg)

            if util.is_DOI(url):
                url = util.get_DOI(url)
            new_kg = describe(url, old_kg)

            triples_before = len(kg)
            triples_after = len(new_kg)
            data = {
                "triples_before": triples_before,
                "triples_after": triples_after,
                "@graph": json.loads(new_kg.serialize(format="json-ld")),
            }
            return data

        get.__doc__ = (
            "Retrieve RDF metadata from URL and try to enrich it with SPARQL request"
        )

        @fc_inspect_namespace.expect(graph_payload)
        def post(self):
            """
            The POST method, taking a rdf graph as input

            Returns:
                dict: A dictionnary containing the eventualy aggregated RDF Graph
            """
            json_data = request.get_json(force=True)
            url = json_data["url"]

            kg = ConjunctiveGraph()
            kg.parse(data=json_data["json-ld"], format="json-ld")
            old_kg = copy.deepcopy(kg)

            if util.is_DOI(url):
                url = util.get_DOI(url)

            new_kg = describe(url, old_kg)
            triples_before = len(kg)
            triples_after = len(new_kg)
            data = {
                "triples_before": triples_before,
                "triples_after": triples_after,
                "@graph": json.loads(new_kg.serialize(format="json-ld")),
            }
            return data

        post.__doc__ = "Try to enrich RDF metadata with SPARQL request"

    Ask.__name__ = Ask.__name__ + describe.__name__.capitalize()


for describe in describe_list:
    generate_ask_api(describe)


@fc_inspect_namespace.route("/inspect_ontologies")
class InspectOntologies(Resource):
    # @fc_inspect_namespace.doc('Evaluates all FAIR metrics at once')
    @fc_inspect_namespace.expect(reqparse)
    def get(self):
        """Inspect if RDF properties and classes are found in ontology registries (OLS, LOV, BioPortal)"""

        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)
        kg = web_res.get_rdf()

        return check_kg(kg, True)


# TODO update method
@fc_inspect_namespace.route("/bioschemas_validation")
class InspectBioschemas(Resource):
    @fc_inspect_namespace.expect(reqparse)
    def get(self):
        """Validate an RDF JSON-LD graph against Bioschemas profiles"""
        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)
        kg = web_res.get_rdf()
        results = {}

        # Evaluate only profile with conformsTo
        results_conformsto = dyn_evaluate_profile_with_conformsto(kg)

        # Try to match and evaluate all found corresponding profiles
        results_type = evaluate_profile_from_type(kg)

        for result_key in results_conformsto.keys():
            results[result_key] = results_conformsto[result_key]

        for result_key in results_type.keys():
            if result_key not in results:
                results[result_key] = results_type[result_key]

        # TODO Try similarity match her for profiles that are not matched

        return results


@fc_inspect_namespace.route("/bioschemas_validation_by_conformsto")
class InspectBioschemasConformsTo(Resource):
    @fc_inspect_namespace.expect(reqparse)
    def get(self):
        """Validate an RDF JSON-LD graph against Bioschemas profiles using dct:conformsTo"""
        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)
        kg = web_res.get_rdf()

        # Evaluate only profile with conformsTo
        results_conformsto = dyn_evaluate_profile_with_conformsto(kg)

        # TODO Try similarity match her for profiles that are not matched

        return results_conformsto


@fc_inspect_namespace.route("/bioschemas_validation_by_types")
class InspectBioschemasTypesMatch(Resource):
    @fc_inspect_namespace.expect(reqparse)
    def get(self):
        """Validate an RDF JSON-LD graph against Bioschemas profiles using types"""
        args = reqparse.parse_args()
        url = args["url"]

        web_res = WebResource(url)
        kg = web_res.get_rdf()

        # Try to match and evaluate all found corresponding profiles
        results_type = evaluate_profile_from_type(kg)

        # TODO Try similarity match her for profiles that are not matched

        return results_type


def list_routes():
    return ["%s" % rule for rule in app.url_map.iter_rules()]


@socketio.on("webresource")
def handle_webresource(url):
    """
    Warning: Not used yet
    Handler for URL changes in field, might be used to create WebResource object in advance to improve evaluation times

    Args:
        url (str): URL in field that should be evaluated
    """
    dev_logger.info("URL: " + url)


@socketio.on("evaluate_metric")
def handle_metric(json):
    """
    socketio Handler for a metric calculation requests, calling FAIRMetrics API.
    emit the result of the test

    @param json dict Contains the necessary informations to execute evaluate a metric.
    """

    implem = json["implem"]

    metric_name = json["metric_name"]
    client_metric_id = json["id"]
    url = json["url"]

    # if implem == "FAIRMetrics":
    #     evaluate_fairmetrics(json, metric_name, client_metric_id, url)
    if implem == "FAIR-Checker":
        evaluate_fc_metrics(metric_name, client_metric_id, url)
    else:
        print("Invalid implem")
        logging.warning("Invalid implem")


def evaluate_fairmetrics(json, metric_name, client_metric_id, url):
    """
    Function that evaluate a metric from FAIRMetrics and emit the result

    Args:
        json (_type_): _description_
        metric_name (_type_): _description_
        client_metric_id (_type_): _description_
        url (_type_): _description_

    Returns:
        _type_: _description_
    """
    id = METRICS[metric_name].get_id()
    api_url = METRICS[metric_name].get_api()
    principle = METRICS[metric_name].get_principle()

    print("RUNNING " + principle + " for " + str(url))
    emit("running_f")

    try:
        result_object = METRICS[metric_name].evaluate(url)
    except JSONDecodeError:
        print("Error json")
        print("error_" + client_metric_id)
        # emit_json = {
        #     "score": -1,
        #     "comment": "None",
        #     "time": str(evaluation_time),
        #     "name": "",
        #     "csv_line": "\t\t\t"
        # }
        emit("error_" + client_metric_id)

        return False

    # Eval time removing microseconds
    evaluation_time = result_object.get_test_time() - timedelta(
        microseconds=result_object.get_test_time().microseconds
    )
    score = result_object.get_score()

    comment = result_object.get_reason()

    ###

    content_uuid = json["uuid"]

    # remove empty lines from the comment
    comment = test_metric.cleanComment(comment)
    # all_comment = comment
    # select only success and failure
    comment = test_metric.filterComment(comment, "sf")

    # json_result = {
    #     "url": url,
    #     "api_url": api_url,
    #     "principle": principle,
    #     "id": id,
    #     "score": score,
    #     "exec_time": str(evaluation_time),
    #     "date": str(datetime.now().isoformat()),
    # }

    # print(json_result)
    # might be removed
    write_temp_metric_res_file(
        principle, api_url, evaluation_time, score, comment, content_uuid
    )

    principle = principle.split("/")[-1]
    metric_label = api_url.split("/")[-1].replace("gen2_", "")
    name = principle + "_" + metric_label
    csv_line = '"{}"\t"{}"\t"{}"\t"{}"'.format(
        name, score, str(evaluation_time), comment
    )
    # print(name)
    emit_json = {
        "score": score,
        "comment": comment,
        "time": str(evaluation_time),
        "name": name,
        "csv_line": csv_line,
    }

    recommendation(emit_json, metric_name, comment)

    # print(emit_json)
    emit("done_" + client_metric_id, emit_json)
    print("DONE " + principle)


def evaluate_fc_metrics(metric_name, client_metric_id, url):
    """
    Function that evaluate a metric from FAIR-Checker metrics and emit the result

    Args:
        metric_name (str): The name of the metric
        client_metric_id (str): The id of the metric in the UI (to update the correct line)
        url (str): The URI/URL of the resource to be evaluated
    """

    id = METRICS_CUSTOM[metric_name].get_id()
    # Faire une fonction recursive ?
    if cache.get(url) == "pulling":
        while True:
            time.sleep(2)
            if not cache.get(url) == "pulling":
                webresource = cache.get(url)
                break

    elif not isinstance(cache.get(url), WebResource):
        cache.set(url, "pulling")
        webresource = WebResource(url)
        cache.set(url, webresource)
    elif isinstance(cache.get(url), WebResource):
        webresource = cache.get(url)

    METRICS_CUSTOM[metric_name].set_web_resource(webresource)
    name = METRICS_CUSTOM[metric_name].get_principle_tag()
    dev_logger.warning("Evaluating FC metric: " + name)

    result = METRICS_CUSTOM[metric_name].evaluate()

    score = result.get_score()
    # Eval time removing microseconds
    evaluation_time = result.get_test_time() - timedelta(
        microseconds=result.get_test_time().microseconds
    )
    comment = result.get_log_html()

    recommendation = result.get_recommendation()

    # Persist Evaluation oject in MongoDB
    result.persist(str(SOURCE.UI))

    id = METRICS_CUSTOM[metric_name].get_id()
    csv_line = '"{}"\t"{}"\t"{}"\t"{}"\t"{}"'.format(
        id, name, score, str(evaluation_time), comment
    )
    csv_line = {
        "id": id,
        "name": name,
        "score": score,
        "time": str(evaluation_time),
        "comment": comment,
    }
    emit_json = {
        "score": str(score),
        "time": str(evaluation_time),
        "comment": comment,
        "recommendation": recommendation,
        "csv_line": csv_line,
    }
    emit("done_" + client_metric_id, emit_json)
    dev_logger.info("DONE FC metric: " + name)


### To Remove ?
@DeprecationWarning
@socketio.on("quick_structured_data_search")
def handle_quick_structured_data_search(url):
    if url == "":
        return False

    extruct_rdf = util.extract_rdf_from_html(url)
    graph = util.extruct_to_rdf(extruct_rdf)
    result_list = util.rdf_to_triple_list(graph)
    emit("done_data_search", result_list)


def recommendation(emit_json, metric_name, comment):
    """
    Recommendations for FAIRMetrics (Mark D W.)
    Emit the result to the Check UI

    Args:
        emit_json (dict): Dictionnary containing results of evaluation
        metric_name (str): Name of the evaluated metric
        comment (str): Explaination of what the metric did (evaluation + results)
    """
    recommendation_dict = {
        # F1
        "unique_identifier": {
            "did not match any known identification system (tested inchi, doi, "
            "handle, uri) and therefore did not pass this metric.  If you think"
            " this is an error, please contact the FAIR Metrics group "
            "(http://fairmetrics.org).": "You may use another identification "
            "scheme for your resource. For instance, provide a DOI, a URI "
            "(https://www.w3.org/wiki/URI) or a pubmed id (PMID) for an academic"
            "paper. Also, look at the FAIR Cookbook: "
            "https://fairplus.github.io/the-fair-cookbook/content/recipes/findability/identifiers.html",
        },
        "data_identifier_persistence": {
            "FAILURE: The identifier": "You may use another identification scheme for your resource. For instance, provide a DOI, a URI (https://www.w3.org/wiki/URI) or a pubmed id for an academic paper.",
            "FAILURE: Was unable to locate the data identifier in the metadata using any (common) property/predicate reserved": "Ensure that the resource identifier is part of your web page meta-data (RDFa, embedded JSON-LD, microdata, etc.)",
            "FAILURE: The GUID identifier of the data": "Ensure that the resource identifier, part of your web page meta-data (RDFa, embedded JSON-LD, microdata, etc.) is well formed (DOI, URI, PMID, etc.). ",
            "FAILURE: The GUID does not conform with any known permanent-URL system.": "Ensure that the used identification scheme is permanent. For instance DOIs or PURLs are sustainable over the long term.",
        },
        "identifier_persistence": {
            "The GUID identifier of the metadata": "Ensure that meta-data describing your resource use permanent and well fprmed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: The metadata GUID does not conform with any known permanent-URL system.": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
        },
        # F2
        "grounded_metadata": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: no linked-data style structured metadata found.": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
        },
        "structured_metadata": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: no structured metadata found": "Ensure that meta-data describing your resource use a machine readable format such as JSON or RDF.",
        },
        # F3
        "data_identifier_explicitly_in_metadata": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: Was unable to locate the data identifier in the metadata using any (common) property/predicate reserved": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
        },
        "metadata_identifier_explicitly_in_metadata": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: No metadata identifiers were found in the metadata record": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: No metadata identifiers were found in the metadata record using predicates": "Ensure that identifiers in your metadata are linked together through typical RDF properties such as (schema:mainEntity, dcterms:identifier, etc.)",
            "FAILURE: linked data metadata was not found, so its identifier could not be located": "Ensure that meta-data describing your resource use the RDF machine readable standard.",
            "FAILURE: While (apparent) metadata record identifiers were found": "Ensure that the resource identifier is explicitely referred to in your meta-data. ",
        },
        # F4
        "searchable_in_major_search_engine": {
            "FAILURE: The identifier": "Ensure that the resource identifier, part of your web page meta-data (RDFa, embedded JSON-LD, microdata, etc.) is well formed (DOI, URI, PMID, etc.). Also, see the corresponding FAIR Cookbook page: https://fairplus.github.io/the-fair-cookbook/content/recipes/findability/seo.html",
            "FAILURE: NO ACCESS KEY CONFIGURED FOR BING. This test will now abort with failure": "No recommendation, server side issue",
            "FAILURE: Was unable to discover the metadata record by search in Bing using any method": "Ensure that meta-data describing your resource use the machine readable standards parsed by major search engines such as  schema.org OpenGraph, etc. Also, see the corresponding FAIR Cookbook page: https://fairplus.github.io/the-fair-cookbook/content/recipes/findability/seo.html",
        },
        # A1.1
        "uses_open_free_protocol_for_metadata_retrieval": {
            "FAILURE: The identifier ": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
        },
        "uses_open_free_protocol_for_data_retrieval": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: Was unable to locate the data identifier in the metadata using any (common) property/predicate reserved for this purpose": "Ensure that identifiers in your metadata are linked together through typical RDF properties such as (schema:mainEntity, dcterms:identifier, etc.)",
        },
        # A1.2
        "data_authentication_and_authorization": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: No data identifier was found in the metadata record": "Ensure that identifiers in your metadata are linked together through typical RDF properties such as (schema:mainEntity, dcterms:identifier, etc.)",
        },
        "metadata_authentication_and_authorization": {
            "FAILURE: The GUID identifier of the metadata": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
        },
        # A2
        "metadata_persistence": {
            "FAILURE: The GUID identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: http://www.w3.org/2000/10/swap/pim/doc#persistencePolicy states that the range of the property must be a resource.": "Ensure that a peristence policy predicate is used in the resource metadata : http://www.w3.org/2000/10/swap/pim/doc#persistencePolicy ",
            "FAILURE: Persistence policy did not resolve": "Ensure that a peristence policy predicate is used in the resource metadata : http://www.w3.org/2000/10/swap/pim/doc#persistencePolicy ",
            "FAILURE: was unable to find a persistence policy using any approach": "Ensure that a peristence policy predicate is used in the resource metadata : http://www.w3.org/2000/10/swap/pim/doc#persistencePolicy ",
        },
        # I1
        "data_knowledge_representation_language_weak": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: the data could not be found, or does not appear to be in a recognized knowledge representation language": "Ensure that metadata leverage a standard knowledge representation language such as RDFS, SKOS, OWL, OBO, etc.",
            "FAILURE: The reported content-type header": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher. ",
            "which is not a known Linked Data format": "Ensure that your resource is web accessible and that the HTTP message provides a linked data content-type, e.g. application/ld+json or text/turtle",
            "which is not likely to contain structured data": "Ensure that your resource is web accessible and that the HTTP message provides a structured data content-type, e.g. application/json. You may ask your resource publisher.",
            "FAILURE: The URL to the data is not reporting a Content-Type in its headers.  This test will now halt": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher.",
            "failed to resolve via a HEAD call with headers": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher.",
        },
        "data_knowledge_representation_language_strong": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: the data could not be found, or does not appear to be in a recognized knowledge representation language": "Ensure that metadata leverage a standard knowledge representation language such as RDFS, SKOS, OWL, OBO, etc.",
            "FAILURE: The reported content-type header": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher. ",
            "which is not a known Linked Data format": "Ensure that your resource is web accessible and that the HTTP message provides a linked data content-type, e.g. application/ld+json or text/turtle",
            "which is not likely to contain structured data": "Ensure that your resource is web accessible and that the HTTP message provides a structured data content-type, e.g. application/json. You may ask your resource publisher.",
            "FAILURE: The URL to the data is not reporting a Content-Type in its headers.  This test will now halt": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher.",
            "failed to resolve via a HEAD call with headers": "Ensure that your resource is accessible by an HTTP GET query and provides a content-type header. You may ask to your resource publisher.",
        },
        "metadata_knowledge_representation_language_weak": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: unable to find any kind of structured metadata": "Ensure that meta-data describing your resource use the RDF machine readable standard. Also, you can check the Interoperability recipes of the FAIR Cookbook: https://fairplus.github.io/the-fair-cookbook/content/recipes/interoperability.html",
        },
        "metadata_knowledge_representation_language_strong": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: unable to find any kind of structured metadata": "Ensure that meta-data describing your resource use the RDF machine readable standard. Also, you can check the Interoperability recipes of the FAIR Cookbook: https://fairplus.github.io/the-fair-cookbook/content/recipes/interoperability.html",
        },
        # I2
        "metadata_uses_fair_vocabularies_weak": {
            "FAILURE: The identifier": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: No linked data metadata was found.  Test is exiting": "Ensure that meta-data describing your resource use a machine readable format such as JSON or RDF.",
            "FAILURE: No predicates were found that resolved to Linked Data": "Ensure that meta-data describing your resource use a machine readable format such as JSON or RDF.",
            "The minimum to pass this test is 2/3 (with a minimum of 3 predicates in total)": "Ensure that in your metatdata, at least 2/3rd of your properties should leverage already known voabulary or ontology as registered in OLS, BioPortal, FAIRSharing regitries for instance. Also, check the FAIR Cookbook recipe about ontologies: https://fairplus.github.io/the-fair-cookbook/content/recipes/interoperability/introduction-terminologies-ontologies.html",
        },
        "metadata_uses_fair_vocabularies_strong": {
            "FAILURE: The identifier ": "Ensure that meta-data describing your resource use permanent and well formed identifiers (PURLs, DOIs, etc.)",
            "FAILURE: No linked data metadata was found.  Test is exiting": "Ensure that meta-data describing your resource use a machine readable format such as JSON or RDF.",
            "FAILURE: No predicates were found that resolved to Linked Data.": "Ensure that meta-data describing your resource use a machine readable format such as JSON or RDF.",
            "The minimum to pass this test is 2/3 (with a minimum of 3 predicates in total)": "Ensure that in your metatdata, at least 2/3rd of your properties should leverage already known voabulary or ontology as registered in OLS, BioPortal, FAIRSharing regitries for instance. Also, check the FAIR Cookbook recipe about ontologies: https://fairplus.github.io/the-fair-cookbook/content/recipes/interoperability/introduction-terminologies-ontologies.html",
        },
        # I3
        "metadata_contains_qualified_outward_references": {
            "FAILURE: The identifier ": "You may use another identification scheme for your resource. For instance, provide a DOI, a URI (https://www.w3.org/wiki/URI) or a pubmed id (PMID) for an academic paper.",
            "FAILURE: No linked data was found.  Test is exiting.": "Ensure that your metadata is structured in RDF graphs.",
            "triples discovered in the linked metadata pointed to resources hosted elsewhere.  The minimum to pass this test is 1": "Ensure that your metadata use at least one identifier which is defined in an external resource (e.g. use a UniProt ID in your metadata, the uniprot id being described in UniProt KB)",
        },
        # R1.1
        "metadata_includes_license_weak": {
            "FAILURE: The identifier ": "You may use another identification scheme for your resource. For instance, provide a DOI, a URI (https://www.w3.org/wiki/URI) or a pubmed id (PMID) for an academic paper. Also, you can check the FAIR Cookbook recipe about Licensing: https://fairplus.github.io/the-fair-cookbook/content/recipes/reusability/ATI-licensing.html",
            "FAILURE: No License property was found in the metadata.": "Ensure that a property defining the license of your resoure ispart of your metadata. For instance you can use dcterms:license or schema:license. Also, you can check the FAIR Cookbook recipe about Licensing: https://fairplus.github.io/the-fair-cookbook/content/recipes/reusability/ATI-licensing.html",
        },
        "metadata_includes_license_strong": {
            "FAILURE: The identifier ": "You may use another identification scheme for your resource. For instance, provide a DOI, a URI (https://www.w3.org/wiki/URI) or a pubmed id (PMID) for an academic paper. Also, you can check the FAIR Cookbook recipe about Licensing: https://fairplus.github.io/the-fair-cookbook/content/recipes/reusability/ATI-licensing.html",
            "FAILURE: No License property was found in the metadata.": "Ensure that a property defining the license of your resoure ispart of your metadata. For instance you can use dcterms:license or schema:license. Also, you can check the FAIR Cookbook recipe about Licensing: https://fairplus.github.io/the-fair-cookbook/content/recipes/reusability/ATI-licensing.html",
        },
    }

    # recommendation
    metric_name_key = metric_name.replace(" ", "_").replace("(", "").replace(")", "")
    metric_name_key = metric_name_key.lower()
    # print(metric_name_key)
    # print(recommendation_dict.keys())
    if metric_name_key in recommendation_dict.keys():
        metric_failures = recommendation_dict[metric_name_key]

        for key in metric_failures.keys():
            # print(key)
            # print(comment)
            if key in comment:
                print("found a match!")
                emit_json["recommendation"] = metric_failures[key]
            else:
                print("no match")
    else:
        emit_json["recommendation"] = "Recommendation will be available soon."


### To Remove ?
@DeprecationWarning
def write_temp_metric_res_file(principle, api_url, time, score, comment, content_uuid):
    """
    _summary_

    Args:
        principle (_type_): _description_
        api_url (_type_): _description_
        time (_type_): _description_
        score (_type_): _description_
        comment (_type_): _description_
        content_uuid (_type_): _description_
    """
    global DICT_TEMP_RES
    sid = request.sid
    temp_file_path = "./temp/" + sid

    principle = principle.split("/")[-1]
    api_url = api_url.split("/")[-1].lstrip("gen2_")
    name = principle + "_" + api_url
    # print(name)

    line = '"{}"\t"{}"\t"{}"\t"{}"\n'.format(name, score, str(time), comment)
    # write csv file
    if os.path.exists(temp_file_path):
        with open(temp_file_path, "a") as fp:
            fp.write(line)
            print("success written")

    if content_uuid in DICT_TEMP_RES.keys():
        DICT_TEMP_RES[content_uuid] += line
    else:
        DICT_TEMP_RES[content_uuid] = line


### To remove ? (note used, using Javascript instead)
@DeprecationWarning
@app.route("/check/csv-download/<uuid>")
def csv_download(uuid):
    print("downloading !")
    print(uuid)

    output = io.StringIO()
    output.write(DICT_TEMP_RES[uuid])
    # write file object in BytesIO from StringIO
    content = output.getvalue().encode("utf-8")
    mem = io.BytesIO()
    mem.write(content)
    mem.seek(0)

    # print(json.dumps(DICT_TEMP_RES, sort_keys=True, indent=4))

    try:
        return send_file(
            mem,
            as_attachment=True,
            attachment_filename="results.csv",
            mimetype="text/csv",
            cache_timeout=-1,
        )

    except Exception as e:
        return str(e)


### To remove ?
@DeprecationWarning
@socketio.on("connect")
def handle_connect():
    global FILE_UUID
    print("The random id using uuid() is : ", end="")
    FILE_UUID = str(uuid.uuid1())
    print(FILE_UUID)
    print(request)

    sid = request.sid

    dev_logger.info("Connected with SID " + sid)


### To remove ?
@DeprecationWarning
@socketio.on("disconnect")
def handle_disconnected():
    print("Disconnected")
    sid = request.sid

    time.sleep(5)
    print("Cleaning temp file after disconnect: " + sid)
    if os.path.exists("./temp/" + sid):
        os.remove("./temp/" + sid)


@socketio.on("change_rdf_type")
def handle_change_rdf_type(data):
    """
    Socketio Handler, a function that change the output format of the displayed RDF Graph

    Args:
        data (dict): A dict containing the new RDF Graph format to use for display in Inspect UI
    """
    sid = request.sid
    dev_logger.info("New format to display KG: " + data["rdf_type"])
    RDF_TYPE[sid] = data["rdf_type"]
    kg = KGS[sid]
    nb_triples = len(kg)
    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


@socketio.on("retrieve_embedded_annot_2")
def handle_embedded_annot_2(data):
    """
    Socketio Handler, create an instance of WebResource using the given URL in Inspect UI,
    retrieve RDF metadata and sent it back with emit to the UI

    Args:
        data (dict): Contains the data needed to aggregate (url, etc).
    """

    sid = request.sid
    dev_logger.info("Session ID: " + sid)
    RDF_TYPE[sid] = "turtle"
    uri = str(data["url"])
    dev_logger.info("Retrieve KG for uri: " + uri)

    web_resource = WebResource(uri)
    kg = web_resource.get_rdf()
    nb_triples = len(kg)
    dev_logger.info("Found " + str(nb_triples) + " triples")

    KGS[sid] = kg

    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


### To remove ?
@DeprecationWarning
@socketio.on("update_annot_bioschemas")
def handle_annotationn(data):
    new_kg = rdflib.ConjunctiveGraph()
    new_kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
    new_kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
    new_kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

    # TODO check that url is well formed
    if util.is_URL(data["url"]):
        uri = rdflib.URIRef(data["url"])

        for p in data["warn"].keys():
            if data["warn"][p]:
                value = data["warn"][p]
                if util.is_URL(value):
                    new_kg.add((uri, rdflib.URIRef(p), rdflib.URIRef(value)))
                else:
                    new_kg.add((uri, rdflib.URIRef(p), rdflib.Literal(value)))

        for p in data["err"].keys():
            if data["err"][p]:
                value = data["err"][p]
                if util.is_URL(value):
                    new_kg.add((uri, rdflib.URIRef(p), rdflib.URIRef(value)))
                else:
                    new_kg.add((uri, rdflib.URIRef(p), rdflib.Literal(value)))

        # print("****** Turtle syntax *****")
        # print(new_kg.serialize(format='turtle').decode())
        # print("**************************")

        emit("send_bs_annot", str(new_kg.serialize(format="json-ld")))


@socketio.on("describe_opencitation")
def handle_describe_opencitation(data):
    """
    Socketio Handler, try to aggregate more metadata using Opencitation SPARQL endpoint

    Args:
        data (dict): Dictionnary containing the URL/URI of the resource
    """
    dev_logger.info("Describing with Opencitation")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])

    # check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        dev_logger.info(f"FOUND DOI: {uri}")
    kg = util.describe_opencitation(uri, kg)

    nb_triples = len(kg)
    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


@socketio.on("describe_wikidata")
def handle_describe_wikidata(data):
    """
    Socketio Handler, try to aggregate more metadata using Wikidata SPARQL endpoint

    Args:
        data (dict): Dictionnary containing the URL/URI of the resource
    """
    dev_logger.info("Describing with Wikidata")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])

    # check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        print(f"FOUND DOI: {uri}")
    kg = util.describe_wikidata(uri, kg)
    nb_triples = len(kg)
    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


@socketio.on("describe_loa")
def handle_describe_loa(data):
    """
    Socketio Handler, try to aggregate more metadata using LOA SPARQL endpoint

    Args:
        data (dict): Dictionnary containing the URL/URI of the resource
    """
    dev_logger.info("Describing with LOA")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])

    # check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        print(f"FOUND DOI: {uri}")
    kg = util.describe_openaire(uri, kg)
    nb_triples = len(kg)
    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


### To remove ?
@DeprecationWarning
@socketio.on("retrieve_embedded_annot")
def handle_embedded_annot(data):
    """
    socketio Handler to aggregate original page metadata with sparql endpoints.
    emit the result of sparql requests

    @param data dict Contains the data needed to aggregate (url, etc).
    """
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data["url"])
    print("retrieving embedded annotations for " + uri)
    print("Retrieve KG for uri: " + uri)
    # page = requests.get(uri)
    # html = page.content

    # use selenium to retrieve Javascript genereted content
    html = util.get_html_selenium(uri)

    d = extruct.extract(
        html, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
    )

    kg = ConjunctiveGraph()

    # kg = util.get_rdf_selenium(uri, kg)

    # kg = util.extruct_to_rdf(d)

    base_path = Path(__file__).parent  ## current directory
    static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

    # remove whitespaces from @id values after axtruct
    for key, val in d.items():
        for dict in d[key]:
            list(util.replace_value_char_for_key("@id", dict, " ", "_"))

    for md in d["json-ld"]:
        if "@context" in md.keys():
            if ("https://schema.org" in md["@context"]) or (
                "http://schema.org" in md["@context"]
            ):
                md["@context"] = static_file_path
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    for md in d["rdfa"]:
        if "@context" in md.keys():
            if ("https://schema.org" in md["@context"]) or (
                "http://schema.org" in md["@context"]
            ):
                md["@context"] = static_file_path
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    for md in d["microdata"]:
        if "@context" in md.keys():
            if ("https://schema.org" in md["@context"]) or (
                "http://schema.org" in md["@context"]
            ):
                md["@context"] = static_file_path
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    KGS[sid] = kg

    step += 1
    emit("update_annot", step)
    emit("send_annot", str(kg.serialize(format="turtle").decode()))
    print(len(kg))

    # check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        print(f"FOUND DOI: {uri}")
        # describe on lod.openair

        # @TODO fix wikidata / LOA / etc. access
        kg = util.describe_openaire(uri, kg)
        step += 1
        emit("update_annot", step)
        emit("send_annot", str(kg.serialize(format="turtle").decode()))
        print(len(kg))

    # kg = util.describe_opencitation(uri, kg)
    # step += 1
    # emit('update_annot', step)
    # emit('send_annot', str(kg.serialize(format='turtle').decode()))
    # print(len(kg))
    #
    # kg = util.describe_wikidata(uri, kg)
    # step += 1
    # emit('update_annot', step)
    # emit('send_annot', str(kg.serialize(format='turtle').decode()))
    # print(len(kg))

    kg = util.describe_biotools(uri, kg)
    step += 1
    emit("update_annot", step)
    emit("send_annot", str(kg.serialize(format="turtle").decode()))
    print(f"ended with step {step}")
    print(len(kg))
    print(step)


def check_kg(kg, is_api):
    """
    In Inspect UI, check if classes and properties are found in reference registries
    such as LOV, OLS, BioPortal, or is from Bioschemas.

    Args:
        kg (rdflib.ConjunctiveGraph): The RDF graph associated with the evaluated resource
        is_api (bool): Indicate if the function if called from the UI or the API

    Returns:
        dict: Result of the classes and properties found or not in each registry to display to the UI
    """

    dev_logger.info("Starting Check Vocabularies")

    query_classes = """
        SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
    """
    query_properties = """
        SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
    """

    table_content = {
        "classes": [],
        "classes_false": [],
        "properties": [],
        "properties_false": [],
        "done": False,
    }

    dev_logger.info("Retrieving all classes in KG")
    qres = kg.query(query_classes)
    for row in qres:
        namespace = urlparse(row["class"]).netloc
        class_entry = {}

        # If property is from Bioschemas, validate the property
        if namespace == "bioschemas.org":
            class_entry = {
                "name": row["class"],
                "tag": {
                    "OLS": None,
                    "LOV": None,
                    "BioPortal": None,
                    "Bioschemas": True,
                },
            }
        else:
            class_entry = {
                "name": row["class"],
                "tag": {"OLS": None, "LOV": None, "BioPortal": None},
            }

        table_content["classes"].append(class_entry)

    dev_logger.info("Retrieving all properties in KG")
    qres = kg.query(query_properties)
    for row in qres:
        namespace = urlparse(row["prop"]).netloc
        property_entry = {}

        if namespace == "bioschemas.org":
            property_entry = {
                "name": row["prop"],
                "tag": {
                    "OLS": None,
                    "LOV": None,
                    "BioPortal": None,
                    "Bioschemas": True,
                },
            }
        else:
            property_entry = {
                "name": row["prop"],
                "tag": {"OLS": None, "LOV": None, "BioPortal": None},
            }

        table_content["properties"].append(property_entry)

    if not is_api:
        emit("done_check", table_content)

    dev_logger.info("Checking if classes exists in registries")
    for c in table_content["classes"]:

        c["tag"]["OLS"] = util.ask_OLS(c["name"])
        if not is_api:
            emit("done_check", table_content)

        c["tag"]["LOV"] = util.ask_LOV(c["name"])
        if not is_api:
            emit("done_check", table_content)

        c["tag"]["BioPortal"] = util.ask_BioPortal(c["name"], "class")
        if not is_api:
            emit("done_check", table_content)

        all_false_rule = [
            c["tag"]["OLS"] == False,
            c["tag"]["LOV"] == False,
            c["tag"]["BioPortal"] == False,
        ]

        if all(all_false_rule) and not "Bioschemas" in c["tag"]:
            table_content["classes_false"].append(c["name"])

    dev_logger.info("Checking if properties exists in registries")
    for p in table_content["properties"]:

        p["tag"]["OLS"] = util.ask_OLS(p["name"])
        if not is_api:
            emit("done_check", table_content)

        p["tag"]["LOV"] = util.ask_LOV(p["name"])
        if not is_api:
            emit("done_check", table_content)

        p["tag"]["BioPortal"] = util.ask_BioPortal(p["name"], "property")
        if not is_api:
            emit("done_check", table_content)

        all_false_rule = [
            p["tag"]["OLS"] == False,
            p["tag"]["LOV"] == False,
            p["tag"]["BioPortal"] == False,
        ]
        if all(all_false_rule) and not "Bioschemas" in p["tag"]:
            table_content["properties_false"].append(p["name"])

    table_content["done"] = True

    # Need to emit the result if called from the UI
    if not is_api:
        emit("done_check", table_content)

    dev_logger.info("Check vocabularies done")
    return table_content


@socketio.on("check_kg")
def check_vocabularies():
    """
    Socketio Handler, call the function to check if classes and properties are found in registries (Check Vocabularies).
    """

    # Get the stored Graph to check vocabularies in registries
    sid = request.sid
    kg = KGS[sid]

    check_kg(kg, False)


def evaluate_bioschemas_profiles(kg):
    """
    Evaluate RDF Graph against profiles from Bioschemas using SHACL constraints

    Args:
        kg (rdflib.ConjunctiveGraph): Graph object to evaluate

    Returns:
        dict: The results of the evaluation
    """

    results = {}

    # Evaluate only profile with conformsTo
    results_conformsto = dyn_evaluate_profile_with_conformsto(kg)

    # Try to match and evaluate all found corresponding profiles
    results_type = evaluate_profile_from_type(kg)

    for result_key in results_conformsto.keys():
        results[result_key] = results_conformsto[result_key]

    for result_key in results_type.keys():
        if result_key not in results:
            results[result_key] = results_type[result_key]

    # TODO Try similarity match her for profiles that are not matched

    dev_logger.info("DONE, evaluated " + str(len(results.keys())) + " profiles")

    return results


@socketio.on("check_kg_shape_2")
def check_kg_shape_2():
    """
    Socketio Handler, call the function to evaluate the profiles against the tested resource using SHACL
    """

    dev_logger.info("Starting profiles evaluations with shapes")
    sid = request.sid
    kg = KGS[sid]

    if not kg:
        dev_logger.info("Cannot access current knowledge graph")
    elif len(kg) == 0:
        dev_logger.info("Cannot validate an empty knowledge graph")

    results = evaluate_bioschemas_profiles(kg)

    emit("done_check_shape", results)


### To remove ?
# @DeprecationWarning
def update_bioschemas_valid(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        start_time = time.time()

        value = func(*args, **kwargs)

        # Do something after
        elapsed_time = round((time.time() - start_time), 2)
        logging.info(f"Bioschemas validation processed in {elapsed_time} s")
        # emit("done_check_shape", res, namespace="/validate_bioschemas")
        # socketio.emit("done_check_shape", res, namespace="/inspect")
        return value

    return wrapper_decorator


@app.route("/bioschemas_validation")
@update_bioschemas_valid
def validate_bioschemas():
    """
    Route to directly evaluate RDF Graph against profiles from Bioschemas using SHACL constraints without intermediate steps

    Returns:
        function: Flask template renderer
    """
    uri = request.args.get("url")
    dev_logger.info(f"Validating Bioschemas markup for {uri}")

    kg = WebResource(uri).get_rdf()
    dev_logger.info("Found " + str(len(kg)) + " triples")

    results = evaluate_bioschemas_profiles(kg)

    m = []

    return render_template(
        "bioschemas.html",
        results=results,
        kg=kg,
        f_metrics=m,
        sample_data=sample_resources,
        title="Inspect",
        subtitle="to enhance metadata quality",
        jld=buildJSONLD(),
    )


def buildJSONLD():
    """
    Create the FAIR-Checker pages JSON-LD annotation using schema.org

    Returns:
        str: JSON-LD string describing the FAIR-Checker application
    """

    repo = git.Repo(".")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1]

    jld = {
        "@context": [
            {"sc": "https://schema.org/"},
            {"dct": "http://purl.org/dc/terms/"},
            {"prov": "http://www.w3.org/ns/prov#"},
        ],
        "@type": ["sc:WebApplication", "prov:Entity"],
        "@id": "https://fair-checker.france-bioinformatique.fr",
        "dct:conformsTo": "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE",
        "sc:name": "FAIR-Checker",
        "sc:url": "https://fair-checker.france-bioinformatique.fr",
        "sc:applicationCategory": "Bioinformatics",
        "sc:applicationSubCategory": "Automated FAIR testing",
        "sc:softwareVersion": str(latest_tag),
        "sc:softwareHelp": "https://fair-checker.france-bioinformatique.fr/docs/index.html",
        "sc:codeRepository": "https://github.com/IFB-ElixirFr/FAIR-checker",
        "sc:operatingSystem": "Any",
        "sc:description": """FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.
            Data providers and consumers can check how FAIR are web resources. Developers can explore and inspect metadata exposed in web resources.""",
        "sc:author": [
            {
                "@type": ["sc:Person", "prov:Person"],
                "@id": "https://orcid.org/0000-0003-0676-5461",
                "sc:givenName": "Thomas",
                "sc:familyName": "Rosnet",
                "prov:actedOnBehalfOf": {"@id": "https://ror.org/045f7pv37"},
            },
            {
                "@type": ["sc:Person", "prov:Person"],
                "@id": "https://orcid.org/0000-0002-3597-8557",
                "sc:givenName": "Alban",
                "sc:familyName": "Gaignard",
                "prov:actedOnBehalfOf": {"@id": "https://ror.org/045f7pv37"},
            },
            {
                "@type": ["sc:Person", "prov:Person"],
                "@id": "https://orcid.org/0000-0002-0399-8713",
                "sc:givenName": "Marie-Dominique",
                "sc:familyName": "Devignes",
                "prov:actedOnBehalfOf": {"@id": "https://ror.org/045f7pv37"},
            },
        ],
        "sc:citation": [
            "https://dx.doi.org/10.1038%2Fsdata.2018.118",
            "https://doi.org/10.5281/zenodo.5914307",
            "https://doi.org/10.5281/zenodo.5914367",
        ],
        "sc:license": "https://spdx.org/licenses/MIT.html",
        "prov:wasAttributedTo": [
            {"@id": "https://orcid.org/0000-0003-0676-5461"},
            {"@id": "https://orcid.org/0000-0002-3597-8557"},
            {"@id": "https://orcid.org/0000-0002-0399-8713"},
        ],
    }
    raw_jld = json.dumps(jld)
    return raw_jld


@app.route("/check", methods=["GET"])
def check():
    """
    Route to load the UI Check page elements loading informations from FAIR-Checker metrics.
    Generate a page allowing test of independent metrics.

    Returns:
        function: Flask template renderer
    """
    # unique id to retrieve content results of tests
    content_uuid = str(uuid.uuid1())
    DICT_TEMP_RES[content_uuid] = ""

    raw_jld = buildJSONLD()

    metrics = []

    for key in METRICS_CUSTOM.keys():
        metrics.append(
            {
                "name": METRICS_CUSTOM[key].get_name(),
                "implem": METRICS_CUSTOM[key].get_implem(),
                "description": METRICS_CUSTOM[key].get_desc(),
                "api_url": "API to define",
                "id": METRICS_CUSTOM[key].get_id(),
                "principle": METRICS_CUSTOM[key].get_principle(),
                "principle_tag": METRICS_CUSTOM[key].get_principle_tag(),
                "principle_category": METRICS_CUSTOM[key]
                .get_principle()
                .rsplit("/", 1)[-1][0],
            }
        )

    return make_response(
        render_template(
            "check.html",
            f_metrics=metrics,
            sample_data=sample_resources,
            jld=raw_jld,
            uuid=content_uuid,
            title="Check",
            subtitle="How FAIR is my resource ?",
        )
    )
    # )).headers.add('Access-Control-Allow-Origin', '*')


@app.route("/inspect")
def inspect():
    """
    Route to load the UI Inspect page elements

    Returns:
        function: Flask template renderer
    """
    return render_template(
        "inspect.html",
        sample_data=sample_resources,
        title="Inspect",
        subtitle="to enhance metadata quality",
    )





parser = argparse.ArgumentParser(
    description="""
FAIR-Checker, a web and command line tool to assess FAIRness of web accessible resources.
Usage examples :
    python app.py --web
    python app.py --url http://bio.tools/bwa
    python app.py --bioschemas --url http://bio.tools/bwa

Please report any issue to thomas.rosnet@france-bioinforatique.fr,
or submit an issue to https://github.com/IFB-ElixirFr/fair-checker/issues.
""",
    formatter_class=RawTextHelpFormatter,
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    required=False,
    help="enables debugging logs",
    dest="debug",
)
parser.add_argument(
    "-w",
    "--web",
    action="store_true",
    required=False,
    help="launch FAIR-Checker as a web server",
    dest="web",
)
# nargs='+'
parser.add_argument(
    "-u",
    "--urls",
    nargs="+",
    required=False,
    help="list of URLs to be tested",
    dest="urls",
)
parser.add_argument(
    "-bs",
    "--bioschemas",
    action="store_true",
    required=False,
    help="validate Bioschemas profiles",
    dest="bioschemas",
)


def get_result_style(result) -> str:
    if result == Result.NO:
        return "red"
    elif result == Result.WEAK:
        return "yellow"
    elif result == Result.STRONG:
        return "green"
    return ""


if __name__ == "__main__":

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    print(args)

    if args.update:
        print("UPDATE BS her")

    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    LOGGER = logging.getLogger()
    if not LOGGER.handlers:
        LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    LOGGER.propagate = False

    if args.urls:
        start_time = time.time()

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Findable", justify="right")
        table.add_column("Accessible", justify="right")
        table.add_column("Interoperable", justify="right")
        table.add_column("Reusable", justify="right")

        for url in args.urls:
            logging.debug(f"Testing URL {url}")
            web_res = WebResource(url)

            metrics_collection = []
            for metric_key in METRICS_CUSTOM.keys():
                metric = METRICS_CUSTOM[metric_key]
                metric.set_web_resource(web_res)
                metrics_collection.append(metric)

            if args.bioschemas:
                logging.info("Bioschemas eval")

            else:

                for m in track(metrics_collection, "Processing FAIR metrics ..."):
                    logging.info(m.get_name())
                    res = m.evaluate()
                    if m.get_principle_tag().startswith("F"):
                        table.add_row(
                            Text(
                                m.get_name() + " " + str(res.get_score()),
                                style=get_result_style(res),
                            ),
                            "",
                            "",
                            "",
                        )
                    elif m.get_principle_tag().startswith("A"):
                        table.add_row(
                            "",
                            Text(
                                m.get_name() + " " + str(res.get_score()),
                                style=get_result_style(res),
                            ),
                            "",
                            "",
                        )
                    elif m.get_principle_tag().startswith("I"):
                        table.add_row(
                            "",
                            "",
                            Text(
                                m.get_name() + " " + str(res.get_score()),
                                style=get_result_style(res),
                            ),
                            "",
                        )
                    elif m.get_principle_tag().startswith("R"):
                        table.add_row(
                            "",
                            "",
                            "",
                            Text(
                                f"{m.get_name()} {str(res.get_score())}",
                                style=get_result_style(res),
                            ),
                        )

            console.rule(f"[bold red]FAIRness evaluation for URL {url}")
            console.print(table)
            elapsed_time = round((time.time() - start_time), 2)
            logging.info(f"FAIR metrics evaluated in {elapsed_time} s")

    elif args.web:
        logging.info("Starting webserver")
        try:
            socketio.run(app, host="127.0.0.1", port=5000, debug=True)
        finally:
            browser = WebResource.WEB_BROWSER_HEADLESS
            browser.quit()
