# from time import time
from SPARQLWrapper import SPARQLWrapper, N3
from rdflib import ConjunctiveGraph, URIRef, RDF
import requests
import metrics.statistics as stats

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

from jinja2 import Template
from pyshacl import validate
import extruct
import json
from datetime import datetime, timedelta
from enum import Enum
from cachetools import cached, TTLCache
from flask import Flask
from flask import current_app
from flask_socketio import emit
import logging
import copy
import re
import validators
from urllib.parse import urlparse


class SOURCE(Enum):
    UI = 1
    API = 2

    def __str__(self):
        # return str(self.value)
        return str(self.name)


app = Flask(__name__)

# if app.config["ENV"] == "production":
app.config.from_object("config.Config")
# else:
#     app.config.from_object("config.DevelopmentConfig")

# caching results (timer in config.py)
with app.app_context():
    ttl_cache_timer = current_app.config["CACHE_CONTROLLED_VOCAB_TIMER"]
    ttl_cache_maxsize = current_app.config["CACHE_CONTROLLED_VOCAB_MAXSIZE"]
cache_OLS = TTLCache(
    maxsize=ttl_cache_maxsize, ttl=timedelta(hours=ttl_cache_timer), timer=datetime.now
)
cache_LOV = TTLCache(
    maxsize=ttl_cache_maxsize, ttl=timedelta(hours=ttl_cache_timer), timer=datetime.now
)
cache_BP = TTLCache(
    maxsize=ttl_cache_maxsize, ttl=timedelta(hours=ttl_cache_timer), timer=datetime.now
)

# DOI regex
regex = r"10.\d{4,9}\/[-._;()\/:A-Z0-9]+"


# Dynamicaly generates a table with FAIR metrics implementations
def gen_metrics():
    metrics = []
    METRICS_CUSTOM = app.METRICS_CUSTOM
    for key in app.METRICS_CUSTOM.keys():
        metrics.append(
            {
                "metric": METRICS_CUSTOM[key].get_.metric(),
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
    return metrics


# Describe datacite
def describe_opencitation(uri, g):
    endpoint = "https://opencitations.net/sparql"
    # print(f"SPARQL for [ {uri} ] with endpoint [ {endpoint} ]")
    # sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = (
        """
            PREFIX cito: <http://purl.org/spar/cito/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX datacite: <http://purl.org/spar/datacite/>
            PREFIX literal: <http://www.essepuntato.it/2010/06/literalreification/>
            PREFIX biro: <http://purl.org/spar/biro/>
            PREFIX frbr: <http://purl.org/vocab/frbr/core#>
            PREFIX c4o: <http://purl.org/spar/c4o/>

            DESCRIBE ?x WHERE {
                ?x datacite:hasIdentifier/literal:hasLiteralValue '"""
        + uri
        + """'
            }
    """
    )

    h = {"Accept": "text/turtle"}
    p = {"query": query}

    res = requests.get(endpoint, headers=h, params=p, verify=False)

    new_g = ConjunctiveGraph()
    new_g.parse(data=res.text, format="turtle")
    for s, p, o in new_g:
        g.add((s, p, o, URIRef(uri + "#opencitations")))

    return g


# Describe datacite
def describe_openaire(uri, g):
    logging.debug(f"SPARQL for [ {uri} ] with enpoint [ LOA ]")
    sparql = SPARQLWrapper("http://lod.openaire.eu/sparql")
    sparql.setQuery(
        """
            DESCRIBE ?x WHERE {
            ?x <http://lod.openaire.eu/vocab/resPersistentID> '"""
        + uri
        + """'
            }
    """
    )
    sparql.setReturnFormat(N3)
    results = sparql.query().convert()
    # g.parse(data=results, format="turtle")
    # print("Results: " + str(len(g_len.parse(data=results, format="n3"))))

    new_g = ConjunctiveGraph()
    new_g.parse(data=results, format="turtle")
    for s, p, o in new_g:
        g.add((s, p, o, URIRef(uri + "#openaire")))

    # graph_post_size = len(g)
    # print(f"{graph_post_size - graph_pre_size} added new triples")
    # print(g.serialize(format='turtle').decode())
    return g


# Describe Wikidata
def describe_wikidata(uri, g):
    # g = Graph()
    graph_pre_size = len(g)
    endpoint = "https://query.wikidata.org/sparql"
    logging.debug(f"SPARQL for [ {uri} ] with enpoint [ {endpoint} ]")
    # sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = (
        """
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX p: <http://www.wikidata.org/prop/>
            PREFIX ps: <http://www.wikidata.org/prop/statement/>
            PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX bd: <http://www.bigdata.com/rdf#>

            # retrieve entities by DOIs (P356 property)
            DESCRIBE ?x WHERE {
                ?x wdt:P356 '"""
        + uri
        + """'
            }
    """
    )

    # print(query)

    h = {"Accept": "application/sparql-results+xml"}
    p = {"query": query}

    res = requests.get(endpoint, headers=h, params=p, verify=False)
    # g.parse(data=res.text, format="xml")

    new_g = ConjunctiveGraph()
    new_g.parse(data=res.text, format="xml")
    for s, p, o in new_g:
        g.add((s, p, o, URIRef(uri + "#wikidata")))

    graph_post_size = len(g)
    logging.debug(f"{graph_post_size - graph_pre_size} added new triples")

    # print(g.serialize(format='turtle').decode())
    return g


# Describe a tool based on experimental bio.tools SPARQL endpoint
def describe_biotools(uri, g):
    logging.debug(f"SPARQL for [ {uri} ] with enpoint [ https://130.226.25.41/sparql ]")

    h = {"Accept": "text/turtle"}
    p = {"query": "DESCRIBE <" + uri + ">"}
    res = requests.get(
        "https://130.226.25.41/sparql", headers=h, params=p, verify=False
    )

    g.parse(data=res.text, format="turtle")

    # print(g.serialize(format='turtle').decode())
    return g


def is_URL(any_url):
    if validators.url(any_url):
        return True
    else:
        return False


def is_DOI(uri):
    return bool(re.search(regex, uri, re.MULTILINE | re.IGNORECASE))


def get_DOI(uri):
    match = re.search(regex, uri, re.MULTILINE | re.IGNORECASE)
    return match.group(0)


def remove_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        for key in keys:
            d.pop(key)


@cached(cache_BP)
def ask_BioPortal(uri, type):
    """
    Checks that the URI is registered in one of the ontologies indexed in BioPortal.
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in BioPortal, False otherwise, and None if registry is unreachable.
    """
    remove_key_from_value(cache_BP, None)

    app.logger.debug(f"Call to the BioPortal REST API for [ {uri} ]")
    # print(app.config)
    with app.app_context():
        api_key = current_app.config["BIOPORTAL_APIKEY"]
    h = {"Accept": "application/json", "Authorization": "apikey token=" + str(api_key)}

    if type == "property":
        res = requests.get(
            "https://data.bioontology.org/property_search?q=" + uri,
            headers=h,
            verify=True,
        )
    elif type == "class":
        res = requests.get(
            "https://data.bioontology.org/search?q="
            + uri
            + "&require_exact_match=true",
            headers=h,
            verify=True,
        )
    # print(res)
    if res.status_code == 200:
        return res.json()["totalCount"] > 0
    else:
        app.logger.error("Cound not connect to BioPortal")
        app.logger.error(res.text)
        return None


@cached(cache_OLS)
def ask_OLS(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in OLS.
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in OLS, False otherwise, and None if registry is unreachable.
    """
    remove_key_from_value(cache_OLS, None)

    app.logger.debug(f"Call to the OLS REST API for [ {uri} ]")
    # uri = requests.compat.quote_plus(uri)
    h = {"Accept": "application/json"}
    p = {"iri": uri}
    # TODO we are only checking for properties and not classes, to be fixed.
    res = requests.get(
        "https://www.ebi.ac.uk/ols4/api/properties", headers=h, params=p, verify=True
    )

    if res.status_code == 200:
        return res.json()["page"]["totalElements"] > 0
    else:
        app.logger.error("Cound not connect to OLS")
        app.logger.error(res.text)
        return None


@cached(cache_LOV)
def ask_LOV(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in LOV (Linked Open Vocabularies).
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in LOV, False otherwise, and None if registry is unreachable.
    """
    remove_key_from_value(cache_LOV, None)

    app.logger.debug(
        f"SPARQL for [ {uri} ] with enpoint [ https://lov.linkeddata.es/dataset/lov/sparql ]"
    )

    h = {"Accept": "application/sparql-results+json"}
    p = {"query": "ASK { <" + uri + "> ?p ?o }"}
    res = requests.get(
        "https://lov.linkeddata.es/dataset/lov/sparql", headers=h, params=p, verify=True
    )

    if res.status_code == 200:
        return res.json()["boolean"]
    else:
        app.logger.error("Cound not connect to LOV")
        app.logger.error(res.text)
        return None


def inspect_onto_reg(kg, is_inspect_ui):
    query_classes = """
        SELECT DISTINCT ?class WHERE { GRAPH ?g { ?s rdf:type ?class } } ORDER BY ?class
    """
    query_properties = """
        SELECT DISTINCT ?prop WHERE { GRAPH ?g { ?s ?prop ?o } } ORDER BY ?prop
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

    if is_inspect_ui:
        emit("done_check", table_content)

    for c in table_content["classes"]:
        c["tag"]["OLS"] = ask_OLS(c["name"])
        if is_inspect_ui:
            emit("done_check", table_content)

        c["tag"]["LOV"] = ask_LOV(c["name"])
        if is_inspect_ui:
            emit("done_check", table_content)

        c["tag"]["BioPortal"] = ask_BioPortal(c["name"], "class")
        if is_inspect_ui:
            emit("done_check", table_content)

        all_false_rule = [
            c["tag"]["OLS"] is False,
            c["tag"]["LOV"] is False,
            c["tag"]["BioPortal"] is False,
        ]

        if all(all_false_rule) and "Bioschemas" not in c["tag"]:
            table_content["classes_false"].append(c["name"])

    for p in table_content["properties"]:
        p["tag"]["OLS"] = ask_OLS(p["name"])
        if is_inspect_ui:
            emit("done_check", table_content)

        p["tag"]["LOV"] = ask_LOV(p["name"])
        if is_inspect_ui:
            emit("done_check", table_content)

        p["tag"]["BioPortal"] = ask_BioPortal(p["name"], "property")
        if is_inspect_ui:
            emit("done_check", table_content)

        all_false_rule = [
            p["tag"]["OLS"] is False,
            p["tag"]["LOV"] is False,
            p["tag"]["BioPortal"] is False,
        ]
        if all(all_false_rule) and "Bioschemas" not in p["tag"]:
            table_content["properties_false"].append(p["name"])

    table_content["done"] = True
    if is_inspect_ui:
        emit("done_check", table_content)
    return table_content


# @Deprecated
def gen_shape(property_list=None, class_list=None, recommendation=None):
    """

    @param property_list: a list of OWL/RDF properties
    @param class_list: a list of OWL/RDF classes
    @param recommendation: the message to be displayed during validation
    @return: a SHACL constraint expression to validate RDF graph based on a list or required properties or classes (at least)

    @TODO another method for strong validation (AND)
    """

    return None


# @Deprecated
def shape_checks(kg):
    """

    @param kg:
    @return:
    """

    # types = [
    #     "schema:SoftwareApplication",
    #     "schema:CreativeWork",
    #     "schema:Dataset",
    #     "schema:ScholarlyArticle",
    # ]
    minimal_dataset_properties = [
        "schema:name",
        "schema:description",
        "schema:identifier",
        "schema:keywords",
        "schema:url",
    ]
    recommended_dataset_properties = [
        "schema:license",
        "schema:creator",
        "schema:citation",
    ]

    minimal_software_properties = ["schema:name", "schema:description", "schema:url"]
    recommended_software_properties = [
        "schema:additionalType",
        "schema:applicationCategory",
        "schema:applicationSubCategory",
        "schema:author",
        "schema:license",
        "schema:citation",
        "schema:featureList",
        "schema:softwareVersion",
    ]

    minimal_publication_properties = ["schema:headline", "schema:identifier"]
    recommended_publication_properties = [
        "schema:about",
        "schema:alternateName",
        "schema:author",
        "schema:backstory",
        "schema:citation",
        "schema:dateCreated",
        "schema:dateModified",
        "schema:datePublished",
        "schema:isBasedOn",
        "schema:isPartOf",
        "schema:keywords",
        "schema:license",
        "schema:pageEnd",
        "schema:pageStart",
        "schema:url",
    ]

    shape_template = """
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix schema: <http://schema.org/> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix edam: <http://edamontology.org/> .
    @prefix biotools: <https://bio.tools/ontology/> .

    schema:SoftwareShape
        a sh:NodeShape ;
        sh:targetClass schema:SoftwareApplication ;

        {% for prop_name in data['software_min'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Violation
        ] ;
        {% endfor %}
    .

    schema:SoftwareShape
        a sh:NodeShape ;
        sh:targetClass schema:SoftwareApplication ;

        {% for prop_name in data['software_reco'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Warning
        ] ;
        {% endfor %}
    .

    schema:DatasetShape
        a sh:NodeShape ;
        sh:targetClass schema:Dataset ;

        {% for prop_name in data['dataset_min'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Violation
        ] ;
        {% endfor %}
    .

    schema:DatasetShape
        a sh:NodeShape ;
        sh:targetClass schema:Dataset ;

        {% for prop_name in data['dataset_reco'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Warning
        ] ;
        {% endfor %}
    .

    schema:PaperShape
        a sh:NodeShape ;
        sh:targetClass schema:ScholarlyArticle ;

        {% for prop_name in data['paper_min'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Violation
        ] ;
        {% endfor %}
    .

    schema:PaperShape
        a sh:NodeShape ;
        sh:targetClass schema:ScholarlyArticle ;

        {% for prop_name in data['paper_reco'] %}
        sh:property [
            sh:path {{prop_name}} ;
            sh:minCount 1 ;
            sh:severity sh:Warning
        ] ;
        {% endfor %}
    .

    """

    data = {
        "software_min": minimal_software_properties,
        "software_reco": recommended_software_properties,
        "dataset_min": minimal_dataset_properties,
        "dataset_reco": recommended_dataset_properties,
        "paper_min": minimal_publication_properties,
        "paper_reco": recommended_publication_properties,
    }

    template = Template(shape_template)
    shape = template.render(data=data)
    # print(shape)
    g = ConjunctiveGraph()
    g.parse(data=shape, format="turtle")
    # print(len(g))

    r = validate(
        data_graph=kg,
        data_graph_format="turtle",
        shacl_graph=shape,
        # shacl_graph = my_shacl_constraint,
        shacl_graph_format="turtle",
        ont_graph=None,
        inference="rdfs",
        abort_on_error=False,
        meta_shacl=False,
        debug=True,
    )

    conforms, results_graph, results_text = r

    report_query = """
        SELECT ?node ?path ?severity WHERE {
            ?v rdf:type sh:ValidationReport ;
               sh:result ?r .
            ?r sh:focusNode ?node ;
               sh:sourceShape ?s .
            ?s sh:path ?path ;
               sh:severity ?severity .
        }
    """

    # print("toto")
    # print(results_graph.serialize(format="turtle"))

    results = results_graph.query(report_query)
    warnings = []
    errors = []
    for r in results:
        # print(r)
        if "#Warning" in r["severity"]:
            warnings.append(
                f'Property {r["path"]} <span class="has-text-warning has-text-weight-bold">should be</span> provided'
            )
        if "#Violation" in r["severity"]:
            errors.append(
                f'Property {r["path"]} <span class="has-text-danger has-text-weight-bold">must be</span> provided'
            )

    return warnings, errors


def extract_rdf_from_html(uri):
    page = requests.get(uri)
    html = page.content

    d = extruct.extract(
        html, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
    )
    return d


def extruct_to_rdf(extruct_str):
    g = ConjunctiveGraph()

    for md in extruct_str["json-ld"]:
        g.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    for md in extruct_str["rdfa"]:
        g.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    for md in extruct_str["microdata"]:
        g.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    return g


def rdf_to_triple_list(graph):
    tuple_list = []
    for s, p, o in graph.triples((None, None, None)):
        # print("{} => {} => {}".format(s, p, o))
        tuple_list.append((str(s), str(p), str(o)))

    return tuple_list
    # for s, p, o in graph.triples((None,  RDF.type, None)):
    #     print("{} => {}".format(p, o))


# TODO @Thomas, to be fixed (imports)
# def download_csv(uri):
#
#     client = MongoClient()
#     db = client.fair_checker
#     evaluations = db.evaluations
#
#     a_day_ago = datetime.now() - timedelta(1)
#     pass


def clean_kg_excluding_ns_prefix(kg, ns_prefix) -> ConjunctiveGraph:
    cleaned_kg = copy.deepcopy(kg)
    q_del = (
        'DELETE {?s ?p ?o} WHERE { ?s ?p ?o . FILTER (strstarts(str(?p), "'
        + ns_prefix
        + '"))}'
    )
    cleaned_kg.update(q_del)
    return cleaned_kg


def replace_value_char_for_key(key, var, old_char, new_char):
    if hasattr(var, "items"):
        for k, v in var.items():
            if k == key:
                v = v.replace(old_char, new_char)
                var[k] = v
                yield v
            if isinstance(v, dict):
                for result in replace_value_char_for_key(key, v, old_char, new_char):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in replace_value_char_for_key(
                        key, d, old_char, new_char
                    ):
                        yield result


def gen_usage_statistics():
    logging.info("Retrieving stats")
    stats_dict = {
        "evals_30": stats.evaluations_this_month(),
        "success_30": stats.success_this_month(),
        "failures_30": stats.failures_this_month(),
        "f_success_30": stats.this_month_for_named_metrics(prefix="F", success=1),
        "f_failures_30": stats.this_month_for_named_metrics(prefix="F", success=0),
        "a_success_30": stats.this_month_for_named_metrics(prefix="A", success=1),
        "a_failures_30": stats.this_month_for_named_metrics(prefix="A", success=0),
        "i_success_30": stats.this_month_for_named_metrics(prefix="I", success=1),
        "i_failures_30": stats.this_month_for_named_metrics(prefix="I", success=0),
        "r_success_30": stats.this_month_for_named_metrics(prefix="R", success=1),
        "r_failures_30": stats.this_month_for_named_metrics(prefix="R", success=0),
        "total_monthly": stats.total_monthly(),
    }
    with open("data/usage_stats.json", "w") as outfile:
        json.dump(stats_dict, outfile)
    logging.info("Saved stats")


def list_all_instances(kg):
    #
    # list all typed entities in a knowledge graph
    #
    subjects = []
    for s, p, o in kg.triples((None, RDF.type, None)):
        # print(f"{s} is a {o}")
        subjects.append(s)
    return subjects


ld_eval_prefix = """
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


def get_ld_FC_spec():
    from metrics.FAIRMetricsFactory import FAIRMetricsFactory as FMF

    ld_FC_spec = [
        {
            "id": "F1A",
            "category": "Findable",
            "label": "Unique IDs",
            "definition": "".join(FMF.get_F1A().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_F1A().get_principle(),
        },
        {
            "id": "F1B",
            "category": "Findable",
            "label": "Persistent IDs",
            "definition": "".join(FMF.get_F1B().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_F1B().get_principle(),
        },
        {
            "id": "F2A",
            "category": "Findable",
            "label": "Structured metadata",
            "definition": "".join(FMF.get_F2A().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_F2A().get_principle(),
        },
        {
            "id": "F2B",
            "category": "Findable",
            "label": "Shared vocabularies for metadata",
            "definition": "".join(FMF.get_F2B().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_F2B().get_principle(),
        },
        {
            "id": "A1.1",
            "category": "Accessible",
            "label": "Open resolution protocol",
            "definition": "".join(FMF.get_A11().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_A11().get_principle(),
        },
        {
            "id": "A1.2",
            "category": "Accessible",
            "label": "Authorisation procedure or access rights",
            "definition": "".join(FMF.get_A12().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_A12().get_principle(),
        },
        {
            "id": "I1",
            "category": "Interoperable",
            "label": "Machine readable format",
            "definition": "".join(FMF.get_I1().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_I1().get_principle(),
        },
        {
            "id": "I2",
            "category": "Interoperable",
            "label": "Use shared ontologies",
            "definition": "".join(FMF.get_I2().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_I2().get_principle(),
        },
        {
            "id": "I3",
            "category": "Interoperable",
            "label": "External links",
            "definition": "".join(FMF.get_I3().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_I3().get_principle(),
        },
        {
            "id": "R1.1",
            "category": "Reusable",
            "label": "Metadata includes license",
            "definition": "".join(FMF.get_R11().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_R11().get_principle(),
        },
        {
            "id": "R1.2",
            "category": "Reusable",
            "label": "Metadata includes provenance",
            "definition": "".join(FMF.get_R12().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_R12().get_principle(),
        },
        {
            "id": "R1.3",
            "category": "Reusable",
            "label": "Community standards",
            "definition": "".join(FMF.get_R13().get_desc().strip().splitlines()),
            "seeAlso": FMF.get_R13().get_principle(),
        },
    ]

    return ld_FC_spec


ld_FAIR_Checker_template = """
:$metric_id
    a dqv:Dimension ;
    skos:prefLabel "$metric_label"@en ;
    skos:definition "$metric_definition"@en ;
    dqv:inCategory :$category ;
    rdfs:seeAlso <$seeAlso> ."""

ld_metrics_tpl = """
:$id
    a dqv:QualityMeasurement ;
    dqv:computedOn <$url> ;
    dqv:isMeasurementOf :$dimension ;
    dqv:value "$value"^^xsd:integer ;
    prov:generatedAtTime "$date"^^xsd:dateTime ;
    prov:wasAttributedTo <https://github.com/IFB-ElixirFr/fair-checker> ;
    rdfs:seeAlso <https://doi.org/10.1186/s13326-023-00289-5> ."""
