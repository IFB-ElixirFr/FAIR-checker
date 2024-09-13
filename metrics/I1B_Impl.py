from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2A_Impl import F2A_Impl


@DeprecationWarning
class I1B_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Ontological and machine-resolvable formats"
        self.id = "7"
        self.principle = "https://w3id.org/fair/principles/terms/I1"
        self.principle_tag = "I1B"
        self.implem = "FAIR-Checker"
        self.desc = """
            Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)<br> Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)
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
