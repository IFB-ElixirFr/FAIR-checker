import unittest

from metrics.R2Impl import R2Impl
from metrics.util import describe_loa
from metrics.util import describe_biotools
from metrics.util import describe_wikidata
from metrics.util import describe_opencitation
from metrics.util import is_DOI, get_DOI

from rdflib import Graph, ConjunctiveGraph, Namespace


class KGAugmentTestCase(unittest.TestCase):
    def test_wikidata(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        url = 'http://www.wikidata.org/entity/Q28665865'
        url = "https://search.datacite.org/works/10.7892/boris.108387"

        kg = ConjunctiveGraph()
        kg = describe_wikidata(url, kg)
        print(kg.serialize(format='turtle').decode())

        # self.assertEqual(True, False)

    def test_biotools(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        url = 'http://www.wikidata.org/entity/Q28665865'
        url = "https://workflowhub.eu/workflows/45"
        url = "https://bio.tools/bwa"

        kg = ConjunctiveGraph()
        kg = describe_biotools(url, kg)
        print(kg.serialize(format='turtle').decode())

        # self.assertEqual(True, False)

    def test_loa(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        url = 'http://www.wikidata.org/entity/Q28665865'
        url = "https://workflowhub.eu/workflows/45"
        url = "https://search.datacite.org/works/10.7892/boris.108387"

        # check if id or doi in uri
        if is_DOI(url):
            uri = get_DOI(url)
            print(f'FOUND DOI: {uri}')
            # describe on lod.openair
            kg = ConjunctiveGraph()
            kg = describe_loa(uri, kg)
            print(kg.serialize(format='turtle').decode())

        # self.assertEqual(True, False)

    def test_opencitation(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        url = 'http://www.wikidata.org/entity/Q28665865'
        url = "https://doi.pangaea.de/10.1594/PANGAEA.914331"
        url = "https://search.datacite.org/works/10.7892/boris.108387"

        kg = ConjunctiveGraph()
        kg = describe_opencitation(url, kg)
        print(kg.serialize(format='turtle').decode())

        # self.assertEqual(True, False)
    def test_all(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        url = 'http://www.wikidata.org/entity/Q28665865'
        url = "https://doi.pangaea.de/10.1594/PANGAEA.914331"
        url = "https://search.datacite.org/works/10.7892/boris.108387"
        url = "https://bio.tools/bwa"

        kg = ConjunctiveGraph()
        kg = describe_loa(url, kg)
        kg = describe_opencitation(url, kg)
        kg = describe_wikidata(url, kg)
        kg = describe_biotools(url, kg)
        print(kg.serialize(format='turtle').decode())

        # self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()
