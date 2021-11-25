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
        self.desc = ""

    def weak_evaluate(self, eval=None) -> Evaluation:
        if not eval:
            eval = self.get_evaluation()
        return eval

    def strong_evaluate(self, eval=None) -> Evaluation:
        """
        at least one embedded RDF triple
        """
        if not eval:
            eval = self.get_evaluation()
        kg = self.get_web_resource().get_rdf()

        if len(kg) > 0:
            print(len(kg))
            eval.set_score(2)
            return eval
        eval.set_score(0)
        return eval
