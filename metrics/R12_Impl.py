from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
import validators


class R12_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, web_resource):
        self.name = "R1.2"
        self.desc = "Metadata includes provenance. Evaluate if provenance related properties exist."
        super().__init__(web_resource)

    def strong_evaluate(self) -> bool:
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
            return bool_res

    def weak_evaluate(self) -> bool:
        pass