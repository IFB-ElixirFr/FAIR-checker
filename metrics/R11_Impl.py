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


class R11_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV
    """

    def __init__(self, web_resource):
        super().__init__(web_resource)
        self.name = "Metric name 12"
        self.id = "12"
        self.principle = "https://w3id.org/fair/principles/terms/R1.1"
        self.principle_tag = "R1.1"
        self.implem = "FAIR-Checker"
        self.desc = "Metadata includes license. Evaluate if dct:license or schema:license properties exist."

    def weak_evaluate(self):
        eval = self.get_evaluation()
        return eval

    def strong_evaluate(self):
        eval = self.get_evaluation()
        query_licenses = (
            self.COMMON_SPARQL_PREFIX
            + """
ASK {
    VALUES ?p {schema:license dct:license doap:license dbpedia-owl:license \
    cc:license xhv:license sto:license nie:license } .
    ?s ?p ?o .
    #FILTER( NOT (isBlank(?o))) .
}
        """
        )

        # print(self.rdf_jsonld.serialize(format="turtle").decode())
        res = self.get_web_resource().get_rdf().query(query_licenses)
        for bool_r in res:
            if bool_r:
                return eval.set_score(2)
            else:
                return eval.set_score(0)
