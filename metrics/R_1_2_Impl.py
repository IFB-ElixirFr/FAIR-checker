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


class R_1_2_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV
    """

    def __init__(self, url):
        self.name = "R1.2"
        self.desc = "Metadata includes license. Evaluate if dct:license or schema:license properties exist."
        self.url = url

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
        pass

    def weak_evaluate(self):
        print("Evaluating R1.2")
        self.extract_html_requests()
        self.extract_rdf()

        # TODO define common prefix in the abstract metrics class
        query_licenses = """
            PREFIX schema: <http://schema.org/>
            PREFIX dct: <http://purl.org/dc/terms/> 
            ASK { 
                VALUES ?p {schema:license dct:license} . 
                ?s ?p ?o .
            }
        """

    def strong_evaluate(self):
        print("Evaluating R1.2")
        self.extract_html_requests()
        self.extract_rdf()

        # TODO define common prefix in the abstract metrics class
        # TODO understand why SPARQL filters are not parsed by RDFlib
        query_licenses = """
            PREFIX schema: <http://schema.org/>
            PREFIX dct: <http://purl.org/dc/terms/> 
            ASK { 
                VALUES ?p {schema:license dct:license} . 
                ?s ?p ?o .
                #FILTER( NOT (isBlank(?o))) .
            }
        """

        #print(self.rdf_jsonld.serialize(format="turtle").decode())
        res = self.rdf_jsonld.query(query_licenses)
        for bool_r in res:
            return bool_r