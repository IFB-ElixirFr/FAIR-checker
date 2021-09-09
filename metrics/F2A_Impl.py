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
        self.name = "F2.A"
        self.desc = ""
        super().__init__(web_resource)

    def weak_evaluate(self) -> bool:
        pass

    def strong_evaluate(self) -> bool:
        """
        at least one embedded RDF triple
        """
        kg = self.get_web_resource().get_rdf()
        logging.debug()
        return len(kg) > 0
