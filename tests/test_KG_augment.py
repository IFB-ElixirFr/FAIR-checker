import unittest

from metrics.R2Impl import R2Impl
from metrics.util import describe_wikidata

from rdflib import Graph, ConjunctiveGraph, Namespace


class KGAugmentTestCase(unittest.TestCase):
    def test_something(self):
        # r2 = R2Impl()
        # r2.set_url("https://workflowhub.eu/workflows/45")
        # r2.extract_html_requests()
        # r2.extract_rdf()
        # kg = r2.get_jsonld()
        # print(len(kg))
        # print(kg)
        # print(kg.serialize(format='turtle').decode())

        kg = ConjunctiveGraph()
        describe_wikidata('http://www.wikidata.org/entity/Q28665865', kg)
        print(kg.serialize(format='turtle').decode())

        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()
