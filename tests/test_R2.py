import unittest
import requests
import json
import rdflib
from rdflib import ConjunctiveGraph
from rdflib.compare import to_isomorphic, graph_diff
import pyshacl

import extruct


class MyTestCase(unittest.TestCase):
    def test_something(self):
        uri = 'https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/GANJ7J'

        r = requests.get(uri)
        html = r.content
        d = extruct.extract(html, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')

        print(d)
        kg = ConjunctiveGraph()

        for md in d['json-ld']:
            if '@context' in md.keys():
                print(md['@context'])
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in d['rdfa']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in d['microdata']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        print(f'{len(kg)} retrieved triples in KG')
        print(kg.serialize(format='turtle').decode())
        self.assertEqual(True, True)

        r.connection.close()


if __name__ == '__main__':
    unittest.main()
