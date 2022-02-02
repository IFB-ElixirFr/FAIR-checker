import unittest

from metrics.WebResource import WebResource

from rdflib import Graph, ConjunctiveGraph, Namespace, URIRef, Literal, BNode


class KG_ask(unittest.TestCase):

    kg = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # from https://github.com/RDFLib/rdflib/issues/1003
        rdf_triples_base = """
                @prefix category: <http://example.org/> .
                @prefix dct: <http://purl.org/dc/terms/> .
                @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
                @base <http://example.org/> .

                <> a skos:ConceptScheme ;
                    dct:creator _:BN ;
                    dct:description "Test Description"@en ;
                    dct:source <nick> ;
                    dct:title "Title"@en .
                """
        cls.kg = ConjunctiveGraph()
        cls.kg.parse(data=rdf_triples_base, format="turtle")
        print(cls.kg.serialize(format="turtle"))

    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_ask_filter(self):
        q1 = """
        ASK {
            ?s dct:title ?t .
            FILTER (?t = "Title")
        }
        """
        res = self.kg.query(q1)
        for bool_r in res:
            self.assertFalse(bool_r)

        q2 = """
        ASK {
            ?s dct:title ?t .
            FILTER (?t = "Title"@en)
        }
        """
        res = self.kg.query(q2)
        for bool_r in res:
            self.assertTrue(bool_r)

    def test_ask_filter_notIsBlank(self):
        q3 = """
        ASK {
            ?s dct:title ?t .
            FILTER ( ! isBlank (?s) )
        }
        """
        res = self.kg.query(q3)
        for bool_r in res:
            self.assertTrue(bool_r)

    def test_ask_filter_isIRI(self):
        q4 = """
        ASK {
            ?s dct:title ?t .
            FILTER ( isIRI (?s) )
        }
        """
        res = self.kg.query(q4)
        for bool_r in res:
            self.assertTrue(bool_r)

    def test_ask_filter_isBlank(self):
        q5 = """
        ASK {
            ?s dct:creator ?c .
            FILTER ( isBlank (?c) )
        }
        """
        res = self.kg.query(q5)
        for bool_r in res:
            self.assertTrue(bool_r)


if __name__ == "__main__":
    unittest.main()
