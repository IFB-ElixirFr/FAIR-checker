"""
Unit tests for Evaluation.to_rdf_turtle().

A fake Evaluation is built entirely in-memory (no MongoDB, no HTTP calls).
Flask's app context is pushed so current_app.config["EVAL_URL"] is available,
which to_rdf_turtle() needs to build the subject URI prefix.
"""
import sys
import os
import unittest
import uuid
from datetime import datetime

from rdflib import ConjunctiveGraph, URIRef, Namespace
from rdflib.namespace import RDF, SKOS
from flask import current_app

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from metrics.Evaluation import Evaluation

DQV = Namespace("http://www.w3.org/ns/dqv#")
PROV = Namespace("http://www.w3.org/ns/prov#")
FTR = Namespace("https://w3id.org/ftr#")
TEST_BASE = "https://w3id.org/fairchecker/test/"


def _make_fake_evaluation(metric_tag: str = "F1A", score: str = "1") -> tuple:
    """Return (eval_id, Evaluation) with all fields set, no external calls."""
    eval_id = str(uuid.uuid4())
    ev = Evaluation()
    ev._id = eval_id
    ev.set_target_uri("https://bio.tools/jaspar")
    ev.set_score(score)
    ev.set_metrics(metric_tag)
    ev.set_implem("FAIR-Checker")
    ev.start_time = datetime(2024, 1, 1, 12, 0, 0)
    ev.end_time = datetime(2024, 1, 1, 12, 0, 5)
    return eval_id, ev


class EvaluationRDFTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self._ctx = app.app_context()
        self._ctx.push()
        self.eval_id, self.ev = _make_fake_evaluation()

    def tearDown(self):
        self._ctx.pop()

    # --- helpers ---

    def _turtle_to_graph(self, ttl: str) -> ConjunctiveGraph:
        g = ConjunctiveGraph()
        g.parse(data=ttl, format="turtle")
        return g

    def _eval_uri(self, eval_id: str = None) -> URIRef:
        """Build the evaluation URI using the configured EVAL_URL base."""
        base = current_app.config["EVAL_URL"]
        return URIRef(f"{base}{eval_id or self.eval_id}")

    # --- basic serialisation ---

    def test_to_rdf_turtle_returns_non_empty_string(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        self.assertIsInstance(ttl, str)
        self.assertGreater(len(ttl.strip()), 0)

    def test_to_rdf_turtle_parses_as_valid_turtle(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        self.assertGreater(len(g), 0)

    # --- subject URI ---

    def test_eval_subject_uri_is_present(self):
        """The evaluation URI built from EVAL_URL + id must appear as a subject."""
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        self.assertIn(self._eval_uri(), set(g.subjects()))

    # --- core triples on the evaluation node ---

    def test_eval_is_typed_as_quality_measurement(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        self.assertIn(
            DQV.QualityMeasurement,
            set(g.objects(self._eval_uri(), RDF.type)),
        )

    def test_eval_computed_on_target_uri(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        self.assertIn(
            URIRef("https://bio.tools/jaspar"),
            set(g.objects(self._eval_uri(), DQV.computedOn)),
        )

    def test_eval_score_value_is_present(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        values = {str(v) for v in g.objects(self._eval_uri(), DQV.value)}
        self.assertIn("1", values)

    def test_eval_attributed_to_fair_checker(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        self.assertIn(
            URIRef("https://github.com/IFB-ElixirFr/fair-checker"),
            set(g.objects(self._eval_uri(), PROV.wasAttributedTo)),
        )

    def test_eval_links_to_metric_test(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        test_uri = URIRef(f"{TEST_BASE}F1A")
        ftr_output = FTR.outputFromTest
        self.assertIn(test_uri, set(g.objects(self._eval_uri(), ftr_output)))

    # --- embedded metric spec block ---

    def test_metric_spec_block_is_included(self):
        """to_rdf_turtle() appends a fct:F1A block describing the test itself."""
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        metric_uri = URIRef(f"{TEST_BASE}F1A")
        self.assertIn(FTR.Test, set(g.objects(metric_uri, RDF.type)))

    def test_metric_spec_has_pref_label(self):
        ttl = self.ev.to_rdf_turtle(self.eval_id)
        g = self._turtle_to_graph(ttl)
        metric_uri = URIRef(f"{TEST_BASE}F1A")
        labels = {str(v) for v in g.objects(metric_uri, SKOS.prefLabel)}
        self.assertTrue(len(labels) > 0, "fct:F1A should have at least one skos:prefLabel")

    # --- score boundary ---

    def test_score_zero_is_serialised(self):
        """A failing evaluation (score=0) must also produce valid RDF."""
        fail_id, ev_fail = _make_fake_evaluation(metric_tag="F1A", score="0")
        ttl = ev_fail.to_rdf_turtle(fail_id)
        g = self._turtle_to_graph(ttl)
        eval_uri = self._eval_uri(fail_id)
        values = {str(v) for v in g.objects(eval_uri, DQV.value)}
        self.assertIn("0", values)


if __name__ == "__main__":
    unittest.main()
