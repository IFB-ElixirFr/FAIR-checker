from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2B_Impl import F2B_Impl


class R13_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource):
        super().__init__(web_resource)
        self.name = "R1.3"
        self.implem = "F2.B"
        self.desc = ""

    def weak_evaluate(self) -> bool:
        """
        Delegated to F2B
        """
        return F2B_Impl(self.get_web_resource()).weak_evaluate()

    def strong_evaluate(self) -> bool:
        """
        Delegated to F2B
        """
        return F2B_Impl(self.get_web_resource()).strong_evaluate()
