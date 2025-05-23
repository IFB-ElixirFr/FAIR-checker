from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl


@DeprecationWarning
class I1A_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Any structured information"
        self.id = "6"
        self.principle = "https://w3id.org/fair/principles/terms/I1"
        self.principle_tag = "I1A"
        self.implem = "FAIR-Checker"
        self.desc = """
            For the strong assessment, FAIR-Checker verifies that at least one RDF triple can be found in metadata.
        """

    def weak_evaluate(self):
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        eval_from_F2A = F2A_Impl(self.get_web_resource()).weak_evaluate(eval=eval)
        return eval_from_F2A

    def strong_evaluate(self):
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        eval_from_F2A = F2A_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2A
