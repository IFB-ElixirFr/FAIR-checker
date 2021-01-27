from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class R2Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV


    """

    def __init__(self):
        self.name = "R2"

    def evaluate(self):
        print("Evaluating R2")
