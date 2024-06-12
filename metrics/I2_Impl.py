from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.F2B_Impl import F2B_Impl


class I2_Impl(AbstractFAIRMetrics):
    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Use shared ontologies"
        self.id = "8"
        self.principle = "https://w3id.org/fair/principles/terms/I2"
        self.principle_tag = "I2"
        self.implem = "FAIR-Checker"
        self.desc = """
            Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)<br><br>
            Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)
        """

    def weak_evaluate(self):
        """
        Delegated to F2B
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        eval_from_F2B = F2B_Impl(self.get_web_resource()).weak_evaluate(eval=eval)
        return eval_from_F2B

    def strong_evaluate(self):
        """
        Delegated to F2B
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)
        eval_from_F2B = F2B_Impl(self.get_web_resource()).strong_evaluate(eval=eval)
        return eval_from_F2B
