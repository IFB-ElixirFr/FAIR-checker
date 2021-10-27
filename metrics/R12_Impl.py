from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
import validators


class R12_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metric name 13"
        self.id = "13"
        self.principle = "https://w3id.org/fair/principles/terms/R1.2"
        self.principle_tag = "R1.2"
        self.implem = "FAIR-Checker"
        self.desc = "Metadata includes provenance. Evaluate if provenance related properties exist."

    def weak_evaluate(self):
        eval = self.get_evaluation()
        return eval

    def strong_evaluate(self):
        eval = self.get_evaluation()
        query_prov = (
            self.COMMON_SPARQL_PREFIX
            + """ 
ASK { 
    VALUES ?p {prov:wasGeneratedBy prov:wasDerivedFrom prov:wasAttributedTo prov:used prov:wasInformedBy prov:wasAssociatedWith
    prov:startedAtTime prov:endedAtTime
    dct:hasVersion dct:creator dct:contributor 
    pav:hasVersion pav:hasCurrentVersion pav:createdBy pav:authoredBy pav:retrievedFrom pav:importedFrom pav:createdWith 
    pav:retrievedBy pav:importedBy pav:curatedBy pav:createdBy pav:createdAt pav:previousVersion} . 
    ?s ?p ?o .
}
            """
        )

        res = self.get_web_resource().get_rdf().query(query_prov)
        for bool_res in res:
            if bool_res:
                eval.set_score(2)
                return eval
            else:
                eval.set_score(0)
                return eval
