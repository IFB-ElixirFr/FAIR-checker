import unittest
import uuid
from unittest import mock

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.Evaluation import Evaluation


class _BrokenMetric(AbstractFAIRMetrics):
    def weak_evaluate(self) -> Evaluation:
        raise RuntimeError("registry exploded")

    def strong_evaluate(self) -> Evaluation:
        raise RuntimeError("registry exploded")


class EvaluateFailureTestCase(unittest.TestCase):
    def _metric(self, web_resource):
        metric = _BrokenMetric(web_resource)
        metric.principle_tag = f"TEST-{uuid.uuid4()}"
        return metric

    def test_failing_metric_returns_zero_score_with_reason(self):
        web_resource = mock.Mock()
        web_resource.get_url.return_value = "http://example.org/resource"
        result = self._metric(web_resource).evaluate()

        self.assertIsInstance(result, Evaluation)
        self.assertEqual(result.get_score(), "0")
        self.assertIn("RuntimeError: registry exploded", result.get_reason())
        self.assertIn("registry exploded", result.get_log())
        self.assertIn("could not be evaluated", result.get_recommendation())
        self.assertIsNotNone(result.end_time)

    def test_missing_web_resource_is_reported(self):
        result = self._metric(None).evaluate()

        self.assertIsInstance(result, Evaluation)
        self.assertEqual(result.get_score(), "0")
        self.assertIn("no web resource was provided", result.get_reason())

    def test_failure_is_not_cached(self):
        web_resource = mock.Mock()
        web_resource.get_url.return_value = "http://example.org/resource"
        metric = self._metric(web_resource)
        metric.evaluate()
        self.assertIsNone(
            metric.dcache.get(
                metric.get_principle_tag() + "_http://example.org/resource"
            )
        )

    def test_f2b_without_web_resource_raises_explicit_error(self):
        from metrics.F2B_Impl import F2B_Impl

        metric = F2B_Impl(None)
        for evaluate in (metric.weak_evaluate, metric.strong_evaluate):
            with self.assertRaisesRegex(ValueError, "no web resource"):
                evaluate()


if __name__ == "__main__":
    unittest.main()
