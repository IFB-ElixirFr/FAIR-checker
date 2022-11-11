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
    session,
    send_file,
    send_from_directory,
    make_response,
    Blueprint,
    url_for,
)
from flask_restx import Resource, Api, fields
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_caching import Cache
from flask import current_app
from os import environ, path
from dotenv import load_dotenv, dotenv_values
import secrets
import time
import os
import io
import uuid
import argparse
import functools
from argparse import RawTextHelpFormatter
from datetime import datetime
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
from profiles.bioschemas_shape_gen import validate_any_from_KG
from profiles.bioschemas_shape_gen import validate_any_from_microdata
from metrics.util import SOURCE
from urllib.parse import urlparse


import time
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


# blueprint = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    app,
    title="FAIR-Checker API",
    doc="/swagger",
    base_path="/api",
    # base_url='/'
    description=app.config["SERVER_IP"],
)

# app.register_blueprint(blueprint)

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


METRICS = {}
# json_metrics = test_metric.getMetrics()
factory = FAIRMetricsFactory()

# # A DEPLACER AU LANCEMENT DU SERVEUR ######
# METRICS_RES = test_metric.getMetrics()

METRICS_CUSTOM = factory.get_FC_metrics()

for i, key in enumerate(METRICS_CUSTOM):
    METRICS_CUSTOM[key].set_id("FC_" + str(i))

KGS = {}

RDF_TYPE = {}

FILE_UUID = ""

DICT_TEMP_RES = {}

DICT_BANNER_INFO = {"banner_message_info": {}}

# Update banner info with the message in .env
@app.context_processor
def display_info():
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


def validate_status(url):
    return requests.head(url).status_code == 200


@app.context_processor
def display_vocab_status():
    global DICT_BANNER_INFO

    # status_bioportal = validate_status("https://bioportal.bioontology.org/")
    # status_ols = validate_status("https://www.ebi.ac.uk/ols/index")
    # status_lov = validate_status("https://lov.linkeddata.es/dataset/lov/sparql")

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

    return DICT_BANNER_INFO


scheduler = BackgroundScheduler()
scheduler.add_job(func=display_vocab_status, trigger="interval", seconds=600)
# scheduler.add_job(func=display_info, trigger="interval", seconds=600)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.context_processor
def inject_app_version():
    repo = git.Repo(".")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1]
    return dict(version_tag=latest_tag)


@app.context_processor
def inject_jsonld():
    return dict(jld=buildJSONLD())


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/docs/<path:filename>")
def documentation(filename):
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
    return render_template(
        "about.html",
        title="About",
        subtitle="More about FAIR-Checker",
    )


@app.route("/statistics")
def statistics():
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


# my_fields = api.model(
#     "MyModel",
#     {
#         "name": fields.String(description="The name"),
#         "type": fields.String(description="The object type", enum=["A", "B"]),
#         "age": fields.Integer(min=0),
#         "num": fields.Integer(description="The num to get the square of", min=0),
#         # 'url': fields.String(Description='The URL of the resource to be tested', required=True)
#     },
# )

# @api.route("/square/<int:num>")
# class TestSquare(Resource):
#     @api.marshal_with(my_fields)
#     def get(self, num):
#         return {"data": num ** 2}


def generate_check_api(metric):
    @fc_check_namespace.route("/metric_" + metric.get_principle_tag() + "/<path:url>")
    class MetricEval(Resource):
        def get(self, url):

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


@fc_check_namespace.route("/metrics_all/<path:url>")
class MetricEvalAll(Resource):
    def get(self, url):
        """All FAIR metrics"""
        web_res = WebResource(url)

        metrics_collection = []
        metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F2B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

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


@fc_inspect_namespace.route("/get_rdf_metadata/<path:url>")
class RetrieveMetadata(Resource):
    @fc_inspect_namespace.produces(["application/ld+json"])
    def get(self, url):
        """Get RDF metadata in JSON-LD from a web resource"""
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
    @fc_inspect_namespace.route(
        "/" + describe.__name__ + "/<path:url>", methods=["GET"]
    )
    @fc_inspect_namespace.route("/" + describe.__name__ + "/", methods=["POST"])
    # @api.doc(params={"url": "An URL"})
    class Ask(Resource):
        def get(self, url):
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


@fc_inspect_namespace.route("/inspect_ontologies/<path:url>")
class InspectOntologies(Resource):
    def get(self, url):
        """Inspect if RDF properties and classes are found in ontology registries (OLS, LOV, BioPortal)"""
        web_res = WebResource(url)
        kg = web_res.get_rdf()

        return check_kg(kg, True)


def list_routes():
    return ["%s" % rule for rule in app.url_map.iter_rules()]


# def has_no_empty_params(rule):
#     defaults = rule.defaults if rule.defaults is not None else ()
#     arguments = rule.arguments if rule.arguments is not None else ()
#     return len(defaults) >= len(arguments)


# @app.route("/site-map")
# def site_map():
#     links = []
#     for rule in app.url_map.iter_rules():
#         # Filter out rules we can't navigate to in a browser
#         # and rules that require parameters
#         if "GET" in rule.methods and has_no_empty_params(rule):
#             url = url_for(rule.endpoint, **(rule.defaults or {}))
#             links.append((url, rule.endpoint))
#     # links is now a list of url, endpoint tuples
#     return render_template("site_map.html", links=links)


@socketio.on("webresource")
def handle_webresource(url):
    dev_logger.info("A new url to retrieve metadata from !")


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
    dev_logger.info("Testing: " + url)

    # if implem == "FAIRMetrics":
    # evaluate_fairmetrics(json, metric_name, client_metric_id, url)
    if implem == "FAIR-Checker":
        evaluate_fc_metrics(metric_name, client_metric_id, url)
    else:
        print("Invalid implem")
        logging.warning("Invalid implem")


def evaluate_fairmetrics(json, metric_name, client_metric_id, url):
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
    # print("OK FC Metrics")
    # print(cache.get("TOTO"))
    # print(METRICS_CUSTOM)

    dev_logger.info("Evaluating FAIR-Checker metric")
    # prod_logger.info("Evaluating FAIR-Checker metric")
    id = METRICS_CUSTOM[metric_name].get_id()
    dev_logger.info("ID: " + id)
    dev_logger.info("Client ID: " + client_metric_id)
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
    dev_logger.warning("Evaluation: " + metric_name)

    # dev_logger.info("Evaluating: " + metric_name)
    result = METRICS_CUSTOM[metric_name].evaluate()

    score = result.get_score()
    # Eval time removing microseconds
    evaluation_time = result.get_test_time() - timedelta(
        microseconds=result.get_test_time().microseconds
    )
    # comment = result.get_reason()
    comment = result.get_log_html()

    recommendation = result.get_recommendation()
    # print(recommendation)

    # Persist Evaluation oject in MongoDB
    implem = METRICS_CUSTOM[metric_name].get_implem()
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
        # "name": name,
    }
    emit("done_" + client_metric_id, emit_json)
    dev_logger.info("DONE our own metric !")


@socketio.on("quick_structured_data_search")
def handle_quick_structured_data_search(url):
    if url == "":
        return False

    extruct_rdf = util.extract_rdf_from_html(url)
    graph = util.extruct_to_rdf(extruct_rdf)
    result_list = util.rdf_to_triple_list(graph)
    emit("done_data_search", result_list)


def recommendation(emit_json, metric_name, comment):

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


def write_temp_metric_res_file(principle, api_url, time, score, comment, content_uuid):
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


@socketio.on("download_csv")
def handle_csv_download():

    # temp_file_path = "./temp/" + FILE_UUID

    print("Received download request from " + FILE_UUID)
    # csv_download(temp_file_path)


@app.route("/base_metrics/csv-download/<uuid>")
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
        # return send_from_directory(
        #     "./temp/" + sid,
        #     as_attachment=True,
        #     attachment_filename='metrics_results.csv',
        #     mimetype='text/csv'
        # )
    except Exception as e:
        return str(e)


# # not working
# @socketio.on("connected")
# def handle_connected(json):

#     print(request.namespace.socket.sessid)
#     print(request.namespace)


@socketio.on("connect")
def handle_connect():
    global FILE_UUID
    print("The random id using uuid() is : ", end="")
    FILE_UUID = str(uuid.uuid1())
    print(FILE_UUID)
    print(request)

    sid = request.sid

    dev_logger.info("Connected with SID " + sid)

    # Creates a new temp file
    # with open("./temp/" + sid, 'w') as fp:
    #     pass


@socketio.on("disconnect")
def handle_disconnected():
    print("Disconnected")
    sid = request.sid

    time.sleep(5)
    print("Cleaning temp file after disconnect: " + sid)
    if os.path.exists("./temp/" + sid):
        os.remove("./temp/" + sid)


#######################################
#######################################


@socketio.on("get_latest_triples")
def handle_get_latest_triples():
    sid = request.sid
    kg = KGS[sid]

    list_triples = []
    for s, p, o in kg.triples((None, None, None)):
        triple = {"subject": s, "predicate": p, "object": o}
        list_triples.append(triple)
    emit("send_triples", {"triples": list_triples})


@socketio.on("change_rdf_type")
def handle_change_rdf_type(data):

    sid = request.sid
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
    socketio Handler to aggregate original page metadata with sparql endpoints.
    emit the result of sparql requests

    @param data dict Contains the data needed to aggregate (url, etc).
    """
    # step = 0
    print("handle annot_2")
    sid = request.sid
    print(sid)
    RDF_TYPE[sid] = "turtle"
    uri = str(data["url"])
    print("retrieving embedded annotations for " + uri)
    print("Retrieve KG for uri: " + uri)

    web_resource = WebResource(uri)
    kg = web_resource.get_rdf()
    nb_triples = len(kg)
    print(nb_triples)

    KGS[sid] = kg

    emit(
        "send_annot_2",
        {
            "kg": str(kg.serialize(format=RDF_TYPE[sid])),
            "nb_triples": nb_triples,
        },
    )


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
    print("describing opencitation")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])
    graph = str(data["graph"])
    # kg = ConjunctiveGraph()
    # kg.parse(data=graph, format="turtle")
    # check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        print(f"FOUND DOI: {uri}")
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
    print("describing wikidata")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])
    graph = str(data["graph"])
    # kg = ConjunctiveGraph()
    # kg.parse(data=graph, format="turtle")
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
    print("describing loa")
    sid = request.sid
    kg = KGS[sid]
    uri = str(data["url"])
    graph = str(data["graph"])
    # kg = ConjunctiveGraph()
    # kg.parse(data=graph, format="turtle")
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


@socketio.on("complete_kg")
def handle_complete_kg(json):
    print("completing KG for " + str(json["url"]))


def check_kg(kg, is_api):
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
    qres = kg.query(query_classes)
    for row in qres:
        namespace = urlparse(row["class"]).netloc
        class_entry = {}

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
    if not is_api:
        emit("done_check", table_content)
    return table_content


@socketio.on("check_kg")
def check_vocabularies(data):
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data["url"])
    if not sid in KGS.keys():
        handle_embedded_annot(data)
    elif not KGS[sid]:
        handle_embedded_annot(data)
    kg = KGS[sid]

    check_kg(kg, False)


@DeprecationWarning
@socketio.on("check_kg_shape")
def check_kg_shape(data):
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data["url"])
    if not sid in KGS.keys():
        handle_embedded_annot(data)
    elif not KGS[sid]:
        handle_embedded_annot(data)
    kg = KGS[sid]

    # TODO replace this code with profiles.bioschemas_shape_gen
    warnings, errors = util.shape_checks(kg)
    data = {"errors": errors, "warnings": warnings}
    emit("done_check_shape", data)

    # replacement
    # results = bioschemas_shape.validate_any_from_microdata(uri)
    # print(results)


@socketio.on("check_kg_shape_2")
def check_kg_shape_2(data):
    print("shape validation started")
    sid = request.sid
    print(sid)
    kg = KGS[sid]

    if not kg:
        print("cannot access current knowledge graph")
    elif len(kg) == 0:
        print("cannot validate an empty knowledge graph")

    results = validate_any_from_KG(kg)
    emit("done_check_shape", results)


#######################################
#######################################


def cb():
    print("received message originating from server")


def buildJSONLD():
    """
    Create the Advanced page JSON-LD annotation using schema.org

    @return str
    """

    repo = git.Repo(".")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    latest_tag = tags[-1]

    jld = {
        "@context": [
            {"sc": "https://schema.org/"},
            {"dct": "https://purl.org/dc/terms/"},
            {"prov": "http://www.w3.org/ns/prov#"},
        ],
        "@type": ["sc:WebApplication", "prov:Entity"],
        "@id": "https://github.com/IFB-ElixirFr/FAIR-checker",
        "dct:conformsTo": "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE",
        "sc:name": "FAIR-Checker",
        "sc:url": "https://fair-checker.france-bioinformatique.fr",
        "sc:applicationCategory": "Bioinformatics",
        "sc:applicationSubCategory": "Automated FAIR testing",
        "sc:softwareVersion": str(latest_tag),
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
def base_metrics():
    """
    Load the Advanced page elements loading informations from FAIRMetrics API.
    Generate a page allowing test of independent metrics.

    @return render_template
    """
    # unique id to retrieve content results of tests
    content_uuid = str(uuid.uuid1())
    DICT_TEMP_RES[content_uuid] = ""

    # print(str(session.items()))
    # sid = request.sid
    # return render_template('test_asynch.html')
    # metrics = []
    #
    # metrics_res = METRICS_RES
    #
    # for metric in metrics_res:
    #     # remove "FAIR Metrics Gen2" from metric name
    #     name = metric["name"].replace('FAIR Metrics Gen2- ','')
    #     # same but other syntax because of typo
    #     name = name.replace('FAIR Metrics Gen2 - ','')
    #     metrics.append({
    #         "name": name,
    #         "description": metric["description"],
    #         "api_url": metric["smarturl"],
    #         "id": "metric_" + metric["@id"].rsplit('/', 1)[-1],
    #         "principle": metric["principle"],
    #         "principle_tag": metric["principle"].rsplit('/', 1)[-1],
    #         "principle_category": metric["principle"].rsplit('/', 1)[-1][0],
    #     })

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

    # for key in METRICS.keys():
    #     print()
    #     metrics.append(
    #         {
    #             "name": METRICS[key].get_name(),
    #             "implem": METRICS[key].get_implem(),
    #             "description": METRICS[key].get_desc(),
    #             "api_url": METRICS[key].get_api(),
    #             "id": "metric_" + METRICS[key].get_id().rsplit("/", 1)[-1],
    #             "principle": METRICS[key].get_principle(),
    #             "principle_tag": METRICS[key].get_principle().rsplit("/", 1)[-1],
    #             "principle_category": METRICS[key]
    #             .get_principle()
    #             .rsplit("/", 1)[-1][0],
    #         }
    #     )

    # response =
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


# @app.after_request
# def after_request(response):
#   response.headers.add('Access-Control-Allow-Origin', '*')
#   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#   return response


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


@app.route("/validate_bioschemas")
@update_bioschemas_valid
def validate_bioschemas():
    uri = request.args.get("uri")
    logging.debug(f"Validating Bioschemas markup fr {uri}")

    res, kg = validate_any_from_microdata(input_url=uri)

    m = []
    return render_template(
        "bioschemas.html",
        results=res,
        kg=kg,
        f_metrics=m,
        sample_data=sample_resources,
        title="Inspect",
        subtitle="to enhance metadata quality",
        jld=buildJSONLD(),
    )


@app.route("/inspect")
def kg_metrics_2():
    # m = [{  "name": "i1",
    #         "description": "desc i1",
    #         "id": "metric_i1",
    #         "principle": "principle for i1" }]
    m = []
    return render_template(
        "inspect.html",
        f_metrics=m,
        sample_data=sample_resources,
        title="Inspect",
        subtitle="to enhance metadata quality",
    )


@app.route("/test_url", methods=["POST"])
def testUrl():
    test_url = request.form.get("url")

    number = test_metric.getMetrics()
    # socketio.emit('newnumber', {'number': number}, namespace='/test')
    socketio.emit("my response", {"data": "got it!"}, namespace="/test")

    (
        headers_list,
        descriptions_list,
        test_score_list,
        time_list,
        comments_list,
    ) = test_metric.webTestMetrics(test_url)

    results_list = []
    for i, elem in enumerate(headers_list):
        if i != 0:
            res_dict = {}
            res_dict["header"] = headers_list[i]
            res_dict["score"] = test_score_list[i]
            res_dict["time"] = time_list[i]
            try:
                res_dict["comments"] = comments_list[i].replace("\n", "<br>")
                res_dict["descriptions"] = descriptions_list[i]
            except IndexError:
                res_dict["comments"] = ""
                res_dict["descriptions"] = ""
            results_list.append(res_dict)
        # if i == 4:
        # print(res_dict)

    return render_template(
        "result.html",
        test_url=test_url,
        results_list=results_list,
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
            metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

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
