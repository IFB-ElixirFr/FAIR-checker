from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


class F1Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "F1"

    def evaluate(self):
        print("Evaluating F1")