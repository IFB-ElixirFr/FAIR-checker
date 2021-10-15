import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.FairCheckerExceptions import FairCheckerException


class F2A_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource):
        super().__init__(web_resource)
        # self.name = "F2.A"
        self.id = "3"
        self.principle = "https://w3id.org/fair/principles/terms/F2"
        self.principle_tag = "F2A"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self) -> bool:
        pass

    def strong_evaluate(self) -> bool:
        """
        at least one embedded RDF triple
        """
        eval = self.get_evaluation()
        kg = self.get_web_resource().get_rdf()
        if len(kg) > 0:
            return eval.set_score(2)
        return eval.set_score(0)
