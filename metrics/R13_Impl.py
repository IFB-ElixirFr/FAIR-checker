from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2B_Impl import F2B_Impl


class R13_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metric name 14"
        self.id = "14"
        self.principle = "https://w3id.org/fair/principles/terms/R1.3"
        self.principle_tag = "R1.3"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self):
        """
        Delegated to F2B
        """
        eval = self.get_evaluation()
        eval_from_F2B = F2B_Impl(self.get_web_resource()).weak_evaluate(eval=eval)
        return eval_from_F2B

    def strong_evaluate(self):
        """
        Delegated to F2B
        """
        eval = self.get_evaluation()
        eval_from_F2B = F2B_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2B
