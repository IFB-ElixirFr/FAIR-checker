import logging

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.Evaluation import Evaluation
from metrics.recommendation import json_rec

logger = logging.getLogger(__name__)


class F1A_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Unique IDs"
        self.id = "1"
        self.principle = "https://w3id.org/fair/principles/terms/F1"
        self.principle_tag = "F1A"
        self.implem = "FAIR-Checker"
        self.desc = """
FAIRChecker checks that the resource identifier is a reachable URL. It's better if the URL is persistent (WebID, PURL or DOI).   
        """

    def weak_evaluate(self, eval=None) -> Evaluation:
        if not eval:
            eval = self.get_evaluation()
            eval.set_implem(self.implem)
            eval.set_metrics(self.principle_tag)
        return eval

    def strong_evaluate(self, eval=None) -> Evaluation:
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        status_code = eval.get_web_resource().get_status_code()
        logger.info(
            "Checking if the URL is reachable, status code: " + str(status_code)
        )
        if status_code == 200:
            logger.info("Status code is OK, meaning the url is Unique.")
            eval.set_score(2)
            return eval
        else:
            logger.info(
                "Status code is different than 200, thus, the resource is not reachable."
            )
            eval.set_score(0)
            eval.set_recommendations(json_rec["F1A"]["reco1"])
            return eval

    def blank_node_evaluate(self) -> Evaluation:
        """
        We check here that embedded metadata do not contain RDF blank nodes.
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        query_blank_nodes = """ 
ASK {  
    ?s ?p ?o .
    #FILTER ( isBlank(?s) || isBlank(?p) || isBlank(?o) )
    FILTER ( isBlank(?o) )
}
            """

        eval.log_info("Looking for structured metadata in the web page")
        kg = self.get_web_resource().get_rdf()
        if len(kg) == 0:
            eval.set_score(0)

            # eval.set_reason("No metadata in RDF format found")
            logger.info("No metadata in RDF format found")
            return eval
        else:
            # eval.set_reason(
            #     "Found metadata in RDF format ! (" + str(len(kg)) + " triples)"
            # )
            logger.info("Found metadata in RDF format ! (" + str(len(kg)) + " triples)")
            logger.debug(f"running query:" + f"\n{query_blank_nodes}")
            res = kg.query(query_blank_nodes)
            logger.debug(str(res.serialize(format="json")))
            for bool_res in res:
                if bool_res:
                    # if blank node
                    logger.info("Blank node found, thus ID is not unique")
                    # eval.append_reason("Blank node found, thus ID is not unique")
                    eval.set_score(0)
                else:
                    # if no blank node
                    logger.info(
                        "Blank node found, thus ID is not unique"
                        "No blank node found, meaning every identifiers should be unique"
                    )
                    # eval.append_reason("No blank node found !")
                    eval.set_score(2)
                # print(eval.get_reason())
                return eval

            pass
