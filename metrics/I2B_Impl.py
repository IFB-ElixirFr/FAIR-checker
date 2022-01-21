from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl


class I2B_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Machine-readable vocabularies"
        self.id = "10"
        self.principle = "https://w3id.org/fair/principles/terms/I2"
        self.principle_tag = "I2B"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that at least one RDF triple can be found in metadata. 
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
        Delegated to F2B
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        eval_from_F2A = F2A_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2A
