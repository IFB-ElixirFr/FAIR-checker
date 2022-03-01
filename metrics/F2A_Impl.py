import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.FairCheckerExceptions import FairCheckerException
from metrics.Evaluation import Evaluation
from metrics.recommendation import json_rec


class F2A_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Structured metadata"
        self.id = "3"
        self.principle = "https://w3id.org/fair/principles/terms/F2"
        self.principle_tag = "F2A"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that at least one RDF triple can be found in metadata. 
        """

    def weak_evaluate(self, eval=None) -> Evaluation:
        if not eval:
            eval = self.get_evaluation()
            eval.set_implem(self.implem)
            eval.set_metrics(self.principle_tag)
        return eval

    def strong_evaluate(self, eval=None) -> Evaluation:
        """
        at least one embedded RDF triple
        """

        if not eval:
            eval = self.get_evaluation()
            eval.set_implem(self.implem)
            eval.set_metrics(self.principle_tag)
        eval.log_info(
            "Checking if data is structured, looking for at least one RDF triple..."
        )

        kg = self.get_web_resource().get_rdf()

        if len(kg) > 0:
            eval.log_info(
                str(len(kg))
                + " RDF triples were found, thus data is in a well structured graph format"
            )
            print(len(kg))
            eval.set_score(2)
            return eval
        eval.log_info(
            "No RDF triples found, thus data is probably not structured as needed"
        )
        eval.set_recommendations(json_rec["F2A"]["reco1"])
        eval.set_score(0)
        return eval
