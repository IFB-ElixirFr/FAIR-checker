from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import extruct

import rdflib
from rdflib import ConjunctiveGraph

import json

import validators

from metrics.util import ask_LOV as is_in_LOV


class R2Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV
    """

    def __init__(self):
        self.name = "R2"

        self.api = "api_url_for_R2"

    def get_classes(self):
        query_classes = """
            SELECT DISTINCT ?class WHERE { ?s rdf:type ?class } ORDER BY ?class
        """

        return self.rdf_jsonld.query(query_classes)

    def get_properties(self):
        query_properties = """
            SELECT DISTINCT ?prop WHERE { ?s ?prop ?o } ORDER BY ?prop
        """

        return self.rdf_jsonld.query(query_properties)

    def get_api(self):
        return self.api

    def get_html_source(self):
        return self.html_source

    def get_jsonld(self):
        return self.rdf_jsonld

    def is_valid_uri(self, uri):
        return validators.url(uri)

    def ask_LOV(self, uri):
        return is_in_LOV(uri)

    def evaluate(self):
        print("Evaluating R2")
