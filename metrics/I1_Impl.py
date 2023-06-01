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
        self.name = "Machine readable format"
        self.id = "5"
        self.principle = "https://w3id.org/fair/principles/terms/I1"
        self.principle_tag = "I1"
        self.implem = "FAIR-Checker"
        self.desc = """
            FAIR-Checker verifies that at least one RDF triple can be found in metadata. 
        """

    def weak_evaluate(self):
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        # eval.set_implem(self.implem)
        # eval.set_metrics(self.principle_tag)
        eval_from_F2A = F2A_Impl(self.get_web_resource()).weak_evaluate(eval=eval)
        return eval_from_F2A

    def strong_evaluate(self):
        """
        Delegated to F2A
        """
        eval = self.get_evaluation()
        # eval.set_implem(self.implem)
        # eval.set_metrics(self.principle_tag)
        eval_from_F2A = F2A_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2A
