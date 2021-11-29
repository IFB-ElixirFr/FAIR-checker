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
        self.desc = "FAIRChecker Implem of F1A, more details soon"

    def weak_evaluate(self) -> Evaluation:
        eval = self.get_evaluation()
        return eval

    def strong_evaluate(self) -> Evaluation:
        """
        We check here that embedded metadata do not contain RDF blank nodes.
        """
        eval = self.get_evaluation()

        query_blank_nodes = """ 
ASK {  
    ?s ?p ?o .
    #FILTER ( isBlank(?s) || isBlank(?p) || isBlank(?o) )
    FILTER ( isBlank(?o) )
}
            """
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
                    eval.log_info("No blank node found !")
                    # eval.append_reason("No blank node found !")
                    eval.set_score(2)
                print(eval.get_reason())
                return eval

            pass
