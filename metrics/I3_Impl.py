import logging
from rdflib import URIRef
from urllib.parse import urlparse
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.recommendation import json_rec


class I3_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "External links"
        self.id = "11"
        self.principle = "https://w3id.org/fair/principles/terms/I3"
        self.principle_tag = "I3"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that at least 3 different URL authorities are used in the URIs of RDF metadata.
        """

    def weak_evaluate(self):
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        return eval

    def strong_evaluate(self):
        """at least 3 different URL authorities in URIs"""
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        kg = self.get_web_resource().get_rdf()
        eval.log_info(
            "Checking that at least 3 different URL authorities are used in the URIs of RDF metadata"
        )
        domains = []
        for s, p, o in kg:
            for term in [s, o]:
                if isinstance(term, URIRef):
                    parsed_url = urlparse(term)
                    if parsed_url.netloc not in domains:
                        domains.append(parsed_url.netloc)

        logging.debug(f"Domain names found in URis: {domains}")

        if len(domains) > 3:
            eval.log_info(
                "At least 3 different domains were found in metadata ("
                + str(len(domains))
                + ")"
            )
            eval.set_score(2)
            return eval
        else:
            eval.log_info(
                "Less than 3 different domains were found in metadata ("
                + str(len(domains))
                + ")"
            )
            eval.set_recommendations(json_rec["I3"]["reco1"])
            eval.set_score(0)
            return eval
