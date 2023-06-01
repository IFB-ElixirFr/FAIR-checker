from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
import validators
from metrics.recommendation import json_rec


class A12_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Authorisation procedure or access rights"
        self.id = "16"
        self.principle = "https://w3id.org/fair/principles/terms/A1.2"
        self.principle_tag = "A1.2"
        self.implem = "FAIR-Checker"
        self.desc = """
            The protocol allows for an authentication and authorisation procedure where necessary. <br>
            FAIR-Checker verifies if access rights are specified in metadata through terms 
            odrl:hasPolicy, dct:rights, dct:accessRights, or dct:license. 
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

        checked_properties = """
            odrl:hasPolicy
            dct:rights
            dct:accessRights
            dct:license
            schema:license
        """
        query_prov = (
            self.COMMON_SPARQL_PREFIX
            + """ 
ASK { 
    VALUES ?p { """
            + checked_properties
            + """ } . 
    ?s ?p ?o .
}
            """
        )

        eval.log_info(
            "Checking that at least one of the access policy properties is found in metadata:\n"
            + checked_properties
        )
        res = self.get_web_resource().get_rdf().query(query_prov)
        for bool_res in res:
            if bool_res:
                eval.log_info(
                    "At least one of the access policy properties was found in metadata !"
                )
                eval.set_score(2)
                return eval
            else:
                eval.log_info(
                    "None of the access policy properties were found in metadata !"
                )
                eval.set_recommendations(
                    json_rec["A12"]["reco1"]
                    + checked_properties
                    + """
                """
                )
                eval.set_score(0)
                return eval
