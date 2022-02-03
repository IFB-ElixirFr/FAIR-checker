from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
import requests
from metrics.recommendation import json_rec


class A11_Impl(AbstractFAIRMetrics):
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
        self.name = "Open resolution protocol"
        self.id = "15"
        self.principle = "https://w3id.org/fair/principles/terms/A1.1"
        self.principle_tag = "A1.1"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that the resource is accessible via an open protocol, for instance the protocol needs 
            to be HTTP.
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

        status_code = eval.get_web_resource().get_status_code()
        eval.log_info("Checking if the URL uses HTTP protocol")
        if status_code != 404:
            eval.log_info("The resource use HTTP protocol")
            eval.set_score(2)
            return eval
        elif status_code == 404:
            eval.log_info("The resource can't be found: 404 error")
            eval.set_score(0)
            eval.set_recommendations(
                json_rec["A11"]["reco2"]
            )
            return eval
        else:
            eval.log_info("The resource seems to not be using HTTP protocol")
            eval.set_score(0)
            eval.set_recommendations(json_rec["A11"]["reco1"])
            return eval
