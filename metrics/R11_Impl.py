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
from metrics.recommendation import json_rec


class R11_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV
    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metadata includes license"
        self.id = "12"
        self.principle = "https://w3id.org/fair/principles/terms/R1.1"
        self.principle_tag = "R1.1"
        self.implem = "FAIR-Checker"
        self.desc = """
            Metadata includes license. <br>
            FAIR-Checker verifies that at least one license property from Schema.org, DCTerms, or DOAP ontologies are found in metadata. 
        """

    def weak_evaluate(self):
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        return eval

    def strong_evaluate(self):
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        checked_properties = """
        schema:license 
        dct:license 
        doap:license 
        dbpedia-owl:license 
        cc:license 
        xhv:license 
        sto:license 
        nie:license
        """
        query_licenses = (
            self.COMMON_SPARQL_PREFIX
            + """
ASK {
    VALUES ?p {"""
            + checked_properties
            + """ } .
    ?s ?p ?o .
    #FILTER( NOT (isBlank(?o))) .
}
        """
        )

        eval.log_info(
            "Checking that at least one of the following licence properties is found in metadata:\n"
            + checked_properties
        )
        # print(self.rdf_jsonld.serialize(format="turtle").decode())
        res = self.get_web_resource().get_rdf().query(query_licenses)
        for bool_r in res:
            if bool_r:
                eval.log_info(
                    "At least one of the licence property was found in metadata !"
                )
                eval.set_score(2)
                return eval
            else:
                eval.log_info("None of the licence property were found in metadata")
                eval.set_recommendations(
                    json_rec["R11"]["reco1"]
                    + checked_properties
                    + """
                """
                )
                eval.set_score(0)
                return eval
