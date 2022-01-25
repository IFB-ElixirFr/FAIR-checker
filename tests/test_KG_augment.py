import unittest

import requests

from metrics.util import describe_openaire
from metrics.util import describe_wikidata
from metrics.util import describe_opencitation
from metrics.util import is_DOI, get_DOI
from metrics.WebResource import WebResource

from rdflib import Graph, ConjunctiveGraph, Namespace, URIRef, Literal, BNode


class KGAugmentTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_base_url(selfself):
        # from https://github.com/RDFLib/rdflib/issues/1003
        rdf_triples_base = """
        @prefix category: <http://example.org/> .
        @prefix dct: <http://purl.org/dc/terms/> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
        @base <http://example.org/> .

        <> a skos:ConceptScheme ;
            dct:creator <https://creator.com> ;
            dct:description "Test Description"@en ;
            dct:source <nick> ;
            dct:title "Title"@en .
        """
        kg = ConjunctiveGraph()
        kg.parse(data=rdf_triples_base, format="turtle")
        print(kg.serialize(format="turtle"))

        rdf_triples_NO_base = """
        @prefix category: <http://example.org/> .
        @prefix dct: <http://purl.org/dc/terms/> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

        <> a skos:ConceptScheme ;
            dct:creator <https://creator.com> ;
            dct:description "Test Description"@en ;
            dct:source <nick> ;
            dct:title "Title"@en .
        """
        kg = ConjunctiveGraph()
        kg.parse(data=rdf_triples_NO_base, format="turtle")
        print(kg.serialize(format="turtle"))

        # from scratch
        kg2 = ConjunctiveGraph()
        kg2.add(
            (
                URIRef("http://fair-checker/example/qs"),
                URIRef("http://value"),
                Literal("2"),
            )
        )
        print(kg2.serialize(format="turtle", base="http://fair-checker/example/"))

        kg3 = ConjunctiveGraph()
        kg3.parse(
            data="@base <http://example.org/> . <> a <http://example.org/Class> .",
            format="turtle",
        )
        kg3 = kg3 + kg2
        print(kg3.serialize(format="turtle", base="http://fair-checker/example/"))

    def test_wikidata_alive(self):
        endpoint = "https://query.wikidata.org/sparql"
        uri = "wd:Q1684014"
        h = {"Accept": "application/sparql-results+xml"}
        p = {"query": "DESCRIBE " + uri}

        res = requests.get(endpoint, headers=h, params=p, verify=True)
        print(res.url)
        print(res)
        print(res.text)

        kg = ConjunctiveGraph()
        kg.parse(data=res.text, format="xml")
        print(f"loaded {len(kg)} triples")
        self.assertEqual(len(kg), 55)

    def test_openaire(self):
        url = "https://search.datacite.org/works/10.7892/boris.108387"

        # check if id or doi in uri
        if is_DOI(url):
            uri = get_DOI(url)
            print(f"FOUND DOI: {uri}")
            # describe on lod.openaire
            kg = ConjunctiveGraph()
            kg = describe_openaire(uri, kg)
            print(kg.serialize(format="turtle"))
            self.assertGreaterEqual(len(kg), 10)
        else:
            self.fail()

    def test_opencitation(self):
        test_id = "10.1371/journal.pone.0097158"
        kg = ConjunctiveGraph()
        kg = describe_opencitation(test_id, kg)
        print(kg.serialize(format="turtle"))
        self.assertGreaterEqual(len(kg), 10)

    def test_wikidata_doi(self):
        uri = "10.1126/SCIENCE.97.2524.434"
        kg = ConjunctiveGraph()
        kg = describe_wikidata(uri, kg)
        print(kg.serialize(format="turtle"))
        self.assertGreaterEqual(len(kg), 10)


if __name__ == "__main__":
    unittest.main()
