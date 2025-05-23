from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.recommendation import json_rec


class R12_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metadata includes provenance"
        self.id = "13"
        self.principle = "https://w3id.org/fair/principles/terms/R1.2"
        self.principle_tag = "R1.2"
        self.implem = "FAIR-Checker"
        self.desc = """
            Metadata includes provenance.<br> FAIR-Checker verifies that at least one provenance property from PROV, DCTerms, or PAV ontologies are found in metadata.
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
            prov:wasGeneratedBy 
            prov:wasDerivedFrom 
            prov:wasAttributedTo 
            prov:used 
            prov:wasInformedBy 
            prov:wasAssociatedWith
            prov:startedAtTime 
            prov:endedAtTime
            dct:hasVersion
            dct:isVersionOf 
            dct:creator 
            dct:contributor 
            dct:publisher
            pav:hasVersion
            pav:version 
            pav:hasCurrentVersion 
            pav:createdBy 
            pav:authoredBy 
            pav:retrievedFrom 
            pav:importedFrom 
            pav:createdWith 
            pav:retrievedBy 
            pav:importedBy 
            pav:curatedBy 
            pav:createdAt 
            pav:previousVersion
            schema:creator
            schema:author
            schema:publisher
            schema:provider
            schema:funder
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
            "Checking that at least one of the following provenance properties is found in metadata:\n"
            + checked_properties
        )
        res = self.get_web_resource().get_rdf().query(query_prov)
        for bool_res in res:
            if bool_res:
                eval.log_info(
                    "At least one of the provenance property was found in metadata !"
                )
                eval.set_score(2)
                return eval
            else:
                eval.log_info(
                    "None of the provenance property were found in metadata !"
                )
                eval.set_recommendations(
                    json_rec["R12"]["reco1"]
                    + checked_properties
                    + """
                """
                )
                eval.set_score(0)
                return eval
