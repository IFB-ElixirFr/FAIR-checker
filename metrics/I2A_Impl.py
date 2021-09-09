import logging
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class I2A_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource):
        self.name = "I2A"
        self.desc = ""
        super().__init__(web_resource)

    def weak_evaluate(self) -> bool:
        """
        at least one predicate from {dct:title, rdfs:comment, rdfs:description, rdfs:title, etc.}
        """
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
            return False
        else:
            logging.debug(f"running query:" + f"\n{query_human}")
            res = kg.query(query_human)
            logging.debug(str(res.serialize(format="json")))
            for bool_res in res:
                return bool_res
            pass

    def strong_evaluate(self) -> bool:
        """ """
        pass
