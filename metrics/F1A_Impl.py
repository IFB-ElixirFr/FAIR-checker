import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from datetime import timedelta
from metrics.FairCheckerExceptions import FairCheckerException
from metrics.Evaluation import Evaluation
import validators
import re


class F1A_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Unique IDs"
        self.id = "1"
        self.principle = "https://w3id.org/fair/principles/terms/F1"
        self.principle_tag = "F1A"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIRChecker check that the resource identifier is an URL that can be reach, meaning it is unique, it is even
             better if the URL refer to a DOI.
        """

    def weak_evaluate(self) -> Evaluation:
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        status_code = eval.get_web_resource().get_status_code()
        eval.log_info(
            "Checking if the URL is reachable, status code: " + str(status_code)
        )
        if status_code == 200:
            eval.log_info("Status code is OK, meaning the url is Unique.")
            eval.set_score(1)
            return eval
        else:
            eval.log_info(
                "Status code is different than 200, thus, the resource is not reachable."
            )
            eval.set_score(0)
            eval.set_recommendations("Ensure that the url you used is valid.")
            return eval

    def strong_evaluate(self) -> Evaluation:
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        status_code = eval.get_web_resource().get_status_code()
        doi_regex = "10.\d{4,9}\/[-._;()\/:A-Z0-9]+"

        res = re.search(doi_regex, eval.get_target_uri())

        eval.log_info("Checking if URI contains DOI...")
        print(eval)
        if res:
            eval.log_info("The URI contains a DOI")
            eval.log_info(
                "Checking if the URI is reachable, status code: " + str(status_code)
            )
            if status_code == 200:
                eval.log_info("Status code is OK, meaning the url is Unique.")
                eval.set_score(2)
                return eval
        else:
            eval.log_info("The URI doesn't contains a DOI")
            eval.set_score(0)
            eval.set_recommendations("")
            return eval

    def blank_node_evaluate(self) -> Evaluation:
        """
        We check here that embedded metadata do not contain RDF blank nodes.
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        query_blank_nodes = """ 
ASK {  
    ?s ?p ?o .
    #FILTER ( isBlank(?s) || isBlank(?p) || isBlank(?o) )
    FILTER ( isBlank(?o) )
}
            """

        eval.log_info("Looking for structured metadata in the web page")
        kg = self.get_web_resource().get_rdf()
        if len(kg) == 0:
            eval.set_score(0)

            # eval.set_reason("No metadata in RDF format found")
            eval.log_info("No metadata in RDF format found")
            return eval
        else:
            # eval.set_reason(
            #     "Found metadata in RDF format ! (" + str(len(kg)) + " triples)"
            # )
            eval.log_info(
                "Found metadata in RDF format ! (" + str(len(kg)) + " triples)"
            )
            logging.debug(f"running query:" + f"\n{query_blank_nodes}")
            res = kg.query(query_blank_nodes)
            logging.debug(str(res.serialize(format="json")))
            for bool_res in res:
                if bool_res:
                    # if blank node
                    eval.log_info("Blank node found, thus ID is not unique")
                    # eval.append_reason("Blank node found, thus ID is not unique")
                    eval.set_score(0)
                else:
                    # if no blank node
                    eval.log_info(
                        "No blank node found, meaning every identifiers should be unique"
                    )
                    # eval.append_reason("No blank node found !")
                    eval.set_score(2)
                print(eval.get_reason())
                return eval

            pass
