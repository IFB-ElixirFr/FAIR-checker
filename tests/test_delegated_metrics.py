import unittest

from rdflib import Graph

from metrics.I1_Impl import I1_Impl
from metrics.I2_Impl import I2_Impl
from metrics.R13_Impl import R13_Impl


class StubWebResource:
    """Offline web resource exposing an empty metadata graph."""

    url = "https://example.org/stub"

    def get_url(self):
        return self.url

    def get_rdf(self):
        return Graph()


RECOMMENDATIONS = {"weak": "plugin weak reco", "strong": "plugin strong reco"}


class DelegatedMetricsTestCase(unittest.TestCase):
    """I1, I2 and R13 delegate to F2A / F2B and must pass on their plugin recommendations.

    Regression: the delegate was created with empty recommendations, so the
    evaluation raised KeyError('strong') and the I1 evaluation never finished.
    """

    def build_metric(self, metric_cls):
        metric = metric_cls(StubWebResource())
        # As FAIRMetricsFactory.get_FC_metrics does with the plugin data.
        metric.recommendations = RECOMMENDATIONS
        metric.set_new_evaluation()
        return metric

    def assert_uses_plugin_recommendations(self, metric_cls):
        metric = self.build_metric(metric_cls)

        # Same order as AbstractFAIRMetrics.evaluate(): strong, then weak,
        # both filling the same Evaluation.
        metric.strong_evaluate()
        evaluation = metric.weak_evaluate()

        self.assertEqual(evaluation.get_score(), "0")
        # F2A appends the checked properties to the plugin text.
        self.assertTrue(
            evaluation.get_recommendation().startswith(tuple(RECOMMENDATIONS.values())),
            evaluation.get_recommendation(),
        )

    def test_i1_passes_recommendations_to_f2a(self):
        self.assert_uses_plugin_recommendations(I1_Impl)

    def test_i2_passes_recommendations_to_f2b(self):
        self.assert_uses_plugin_recommendations(I2_Impl)

    def test_r13_passes_recommendations_to_f2b(self):
        self.assert_uses_plugin_recommendations(R13_Impl)
