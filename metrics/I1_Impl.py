from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl


class I1_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource):
        super().__init__(web_resource)
        self.name = "Metric name 5"
        self.id = "5"
        self.principle = "https://w3id.org/fair/principles/terms/I1"
        self.principle_tag = "I1"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self) -> bool:
        """
        Delegated to F2A
        """
        return F2A_Impl(self.get_web_resource()).weak_evaluate()

    def strong_evaluate(self) -> bool:
        """
        Delegated to F2A
        """
        return F2A_Impl(self.get_web_resource()).strong_evaluate()
