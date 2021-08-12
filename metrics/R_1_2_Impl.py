from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class R_1_1_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, url):
        self.name = "R1.2"
        self.desc = "Metadata includes provenance. Evaluate if " " properties exist."
        self.url = url

    def evaluate(self):
        pass

    def evaluate_prov(self):
        print("Evaluating R1.2")
