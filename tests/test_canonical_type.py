import unittest
from rdflib import ConjunctiveGraph, URIRef

from metrics.util import canonical_type_n3


class CanonicalTypeTestCase(unittest.TestCase):
    def setUp(self):
        # Fresh graph, deliberately without sc:/scs: bindings
        self.nm = ConjunctiveGraph().namespace_manager

    def test_https_schema_org(self):
        t = URIRef("https://schema.org/Person")
        self.assertEqual(canonical_type_n3(t, self.nm), "sc:Person")

    def test_http_schema_org(self):
        t = URIRef("http://schema.org/Person")
        self.assertEqual(canonical_type_n3(t, self.nm), "sc:Person")

    def test_https_schema_org_with_scs_binding(self):
        kg = ConjunctiveGraph()
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("scs", URIRef("https://schema.org/"))
        t = URIRef("https://schema.org/Dataset")
        self.assertEqual(canonical_type_n3(t, kg.namespace_manager), "sc:Dataset")

    def test_bioschemas_terms(self):
        kg = ConjunctiveGraph()
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        for iri in (
            "https://bioschemas.org/terms/ComputationalTool",
            "http://bioschemas.org/terms/ComputationalTool",
        ):
            with self.subTest(iri=iri):
                self.assertEqual(
                    canonical_type_n3(URIRef(iri), kg.namespace_manager),
                    "bsc:ComputationalTool",
                )

    def test_other_namespace_unchanged(self):
        t = URIRef("http://example.org/Thing")
        self.assertEqual(canonical_type_n3(t, self.nm), "<http://example.org/Thing>")


if __name__ == "__main__":
    unittest.main()
