import logging
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.recommendation import json_rec


class I2A_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Human-readable vocabularies"
        self.id = "9"
        self.principle = "https://w3id.org/fair/principles/terms/I2"
        self.principle_tag = "I2A"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that at least one property from SKOS or DCTerms or RDFS aimed at  documenting terms such as dct:title, rdfs:label, skos:definition, etc.
        """

    def weak_evaluate(self):
        """
        at least one predicate from {dct:title, rdfs:comment, rdfs:description, rdfs:title, etc.}
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        # List of properties to check
        checked_properties = """dct:title dct:abstract dct:creator dct:license dct:language rdfs:label 
            rdfs:comment rdfs:seeAlso skos:prefLabel skos:altLabel skos:definition skos:example skos:related 
            skos:broader skos:narrower skos:note"""

        query_human = (
            self.COMMON_SPARQL_PREFIX
            + """
        ASK {
            VALUES ?p {"""
            + checked_properties
            + """} .
            
            ?s ?p ?o .
        }
                """
        )

        eval.log_info(
            "Checking that at least one of these properties is used:\n"
            + checked_properties
        )
        kg = self.get_web_resource().get_rdf()
        if len(kg) == 0:
            eval.set_score(0)
            eval.log_info(
                "No RDF metadata were found, thus with existence of the properties can't be verified"
            )
            eval.set_recommendations(json_rec["I2A"]["reco2"])
            return eval
        else:
            logging.debug(f"running query:" + f"\n{query_human}")
            res = kg.query(query_human)
            logging.debug(str(res.serialize(format="json")))
            for bool_res in res:
                if bool_res:
                    eval.log_info(
                        "At least one of the property was found in the RDF metadata"
                    )
                    eval.set_score(1)
                else:
                    eval.log_info(
                        "None of the properties were found in the RDF metadata"
                    )
                    eval.set_score(0)
                    eval.set_recommendations(
                        json_rec["I2A"]["reco1"]
                        + checked_properties
                        + """
                    """
                    )
                return eval

    def strong_evaluate(self):
        """ """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        return eval
