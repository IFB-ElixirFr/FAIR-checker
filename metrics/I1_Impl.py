from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl
from metrics.Evaluation import Evaluation
import logging


class I1_Impl(AbstractFAIRMetrics):

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Metric name 5"
        self.id = "5"
        self.principle = "https://w3id.org/fair/principles/terms/I1"
        self.principle_tag = "I1"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self) -> Evaluation:
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        eval_from_F2A = F2A_Impl(self.get_web_resource()).weak_evaluate(eval=eval)
        return eval_from_F2A

    def strong_evaluate(self) -> Evaluation:
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        eval_from_F2A = F2A_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2A
