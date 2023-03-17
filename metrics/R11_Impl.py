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
    GOAL : Check that metadata include a license
    """

    def __init__(self, web_resource=None):
        """
        The constructor of the metric implementation
        """
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
        """
        The weak evaluation for R11 metric, not doing anything at the moment, only strong is defined

        Returns:
            Evaluation: The Evaluation object containing eventual new informations
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        return eval

    def strong_evaluate(self):
        """
        The strong evaluation for R11 metric, look for at least one license property from Schema.org, DCTerms, etc in metadata.

        Returns:
            Evaluation: The Evaluation object containing eventual new informations
        """

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
