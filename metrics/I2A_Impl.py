import logging
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class I2A_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metric name 9"
        self.id = "9"
        self.principle = "https://w3id.org/fair/principles/terms/I2"
        self.principle_tag = "I2A"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self):
        """
        at least one predicate from {dct:title, rdfs:comment, rdfs:description, rdfs:title, etc.}
        """
        eval = self.get_evaluation()
        query_human = (
            self.COMMON_SPARQL_PREFIX
            + """
        ASK {
            VALUES ?p {dct:title dct:abstract dct:creator dct:license dct:language rdfs:label 
            rdfs:comment rdfs:seeAlso skos:prefLabel skos:altLabel skos:definition skos:example skos:related 
            skos:broader skos:narrower skos:note} .
            
            ?s ?p ?o .
        }
                """
        )

        kg = self.get_web_resource().get_rdf()
        if len(kg) == 0:
            eval.set_score(0)
            return eval
        else:
            logging.debug(f"running query:" + f"\n{query_human}")
            res = kg.query(query_human)
            logging.debug(str(res.serialize(format="json")))
            for bool_res in res:
                if bool_res:
                    eval.set_score(1)
                else:
                    eval.set_score(0)
                return eval

    def strong_evaluate(self):
        """ """
        eval = self.get_evaluation()
        return eval
