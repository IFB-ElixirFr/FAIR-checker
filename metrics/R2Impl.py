from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class R2Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "R2"

    def evaluate(self):
        print("Evaluating R2")
