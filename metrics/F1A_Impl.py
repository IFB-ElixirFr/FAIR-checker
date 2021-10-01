import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.FairCheckerExceptions import FairCheckerException


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

    def weak_evaluate(self) -> bool:
        pass

    def strong_evaluate(self) -> bool:
        """
        We check here that embedded metadata do not contain RDF blank nodes.
        """
        query_blank_nodes = """ 
ASK {  
    ?s ?p ?o .
    #FILTER ( isBlank(?s) || isBlank(?p) || isBlank(?o) )
    FILTER ( isBlank(?o) )
}
            """
        kg = self.get_web_resource().get_rdf()
        if len(kg) == 0:
            return False
        else:
            logging.debug(f"running query:" + f"\n{query_blank_nodes}")
            res = kg.query(query_blank_nodes)
            logging.debug(str(res.serialize(format="json")))
            for bool_res in res:
                return not bool_res
            pass
