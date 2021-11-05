import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.FairCheckerExceptions import FairCheckerException
from metrics.test_metric import testMetric, requestResultSparql
from metrics.Evaluation import Evaluation


class F1B_Impl_fm(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "F1B"
        self.desc = "F1B implemented through the FAIRMetrics API"
        self.url = web_resource.get_url()

    def weak_evaluate(self) -> bool:
        eval = self.get_evaluation()
        return eval

    def strong_evaluate(self) -> bool:
        data = '{"subject": "' + self.url + '"}'
        print("Evaluating " + self.name)

        eval = Evaluation()
        eval.set_start_time()
        eval.result_text = testMetric(
            "https://w3id.org/FAIR_Tests/tests/gen2_metadata_identifier_persistence",
            data,
        )
        logging.debug(eval.result_text)
        eval.set_end_time()
        # evaluation_obj.result_json = json.loads(self.result_text)
        eval.set_score(requestResultSparql(eval.result_text, "ss:SIO_000300"))
        eval.set_reason(requestResultSparql(eval.result_text, "schema:comment"))
        # principle are URLs so we get the last element after the last /
        eval.set_metrics(self.principle.split("/")[-1])
        eval.set_target_uri(self.url)

        if eval.get_score() == "1":
            return True
        else:
            return False
