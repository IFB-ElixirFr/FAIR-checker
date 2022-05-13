from SPARQLWrapper import SPARQLWrapper, N3, JSON, RDF, TURTLE, JSONLD
from rdflib import Graph, ConjunctiveGraph, Namespace
from rdflib.namespace import RDF
import requests
from jinja2 import Template
from pyshacl import validate
import extruct
import json
from pathlib import Path

from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from cachetools import cached, TTLCache
from flask import Flask

import logging

import copy
import re
import validators
from requests.auth import HTTPBasicAuth

from flask import current_app

# caching results during 24 hours
cache_OLS = TTLCache(maxsize=500, ttl=24 * 3600)
cache_LOV = TTLCache(maxsize=500, ttl=24 * 3600)
cache_BP = TTLCache(maxsize=500, ttl=24 * 3600)

app = Flask(__name__)

# if app.config["ENV"] == "production":
app.config.from_object("config.Config")
# else:
#     app.config.from_object("config.DevelopmentConfig")

# DOI regex
regex = r"10.\d{4,9}\/[-._;()\/:A-Z0-9]+"

# Describe datacite
def describe_opencitation(uri, g):
    graph_pre_size = len(g)
    endpoint = "https://opencitations.net/sparql"
    # print(f"SPARQL for [ {uri} ] with enpoint [ {endpoint} ]")
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

    # print(query)

    h = {"Accept": "text/turtle"}
    p = {"query": query}

    res = requests.get(endpoint, headers=h, params=p, verify=False)
    g.parse(data=res.text, format="turtle")

    graph_post_size = len(g)
    # print(f"{graph_post_size - graph_pre_size} added new triples")

    ######################

    # print(g.serialize(format='turtle').decode())
    return g


# Describe lod.openaire
def describe_openaire(uri, g):
    # g = Graph()
    graph_pre_size = len(g)
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

    g_len = Graph()
    sparql.setReturnFormat(N3)
    results = sparql.query().convert()
    # print("Results: " + str(len(g_len.parse(data=results, format="n3"))))
    g.parse(data=results, format="turtle")
    graph_post_size = len(g)
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
    g.parse(data=res.text, format="xml")

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


@cached(cache_BP)
def ask_BioPortal(uri, type):

    logging.debug(f"Call to the BioPortal REST API for [ {uri} ]")
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
        if res.json()["totalCount"] > 0:
            return True
        else:
            return False
    else:
        logging.error("Cound not contact BioPortal")
        logging.error(res.text)
        return False


@cached(cache_OLS)
def ask_OLS(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in OLS.
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in OLS, False otherwise.
    """
    logging.debug(f"Call to the OLS REST API for [ {uri} ]")
    # uri = requests.compat.quote_plus(uri)
    h = {"Accept": "application/json"}
    p = {"iri": uri}
    # TODO we are only checking for properties and not classes, to be fixed.
    res = requests.get(
        "https://www.ebi.ac.uk/ols/api/properties", headers=h, params=p, verify=True
    )
    # print(res.status_code)
    # print(res.headers["content-type"])
    # print(res.headers)
    # print(res.encoding)
    # print(res.json())
    if res.json()["page"]["totalElements"] > 0:
        return True
    else:
        return False


@cached(cache_LOV)
def ask_LOV(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in LOV (Linked Open Vocabularies).
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in LOV, False otherwise.
    """
    logging.debug(
        f"SPARQL for [ {uri} ] with enpoint [ https://lov.linkeddata.es/dataset/lov/sparql ]"
    )

    h = {"Accept": "application/sparql-results+json"}
    p = {"query": "ASK { <" + uri + "> ?p ?o }"}
    res = requests.get(
        "https://lov.linkeddata.es/dataset/lov/sparql", headers=h, params=p, verify=True
    )

    # print(res.text)
    # if res.text.startswith("Error 400: Parse error:"):
    #     return False
    return res.json()["boolean"]


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

    types = [
        "schema:SoftwareApplication",
        "schema:CreativeWork",
        "schema:Dataset",
        "schema:ScholarlyArticle",
    ]
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
