from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl


class I2B_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource):
        super().__init__(web_resource)
        # self.name = "I2B"
        self.id = "10"
        self.principle = "https://w3id.org/fair/principles/terms/I2"
        self.principle_tag = "I2B"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self) -> bool:
        """
        Delegated to F2A
        """
        return F2A_Impl(self.get_web_resource()).weak_evaluate()

    def strong_evaluate(self) -> bool:
        """
        Delegated to F2B
        """
        return F2A_Impl(self.get_web_resource()).strong_evaluate()
