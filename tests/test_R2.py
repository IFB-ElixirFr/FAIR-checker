import unittest
from lxml import html
import requests
import json
import rdflib
from rdflib import ConjunctiveGraph
from rdflib.compare import to_isomorphic, graph_diff
import pyshacl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import extruct

###
### TODO check this issue https://github.com/RDFLib/rdflib-jsonld/issues/84
###
class MyTestCase(unittest.TestCase):

    def test_dynamic_biotools(self):
        uri = 'https://workflowhub.eu/workflows/45'
        # uri = 'https://bio.tools/jaspar'

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        browser = webdriver.Chrome(options = chrome_options)
        browser.get(uri)

        html_source = browser.page_source
        #print(html_source)
        browser.quit()
        tree = html.fromstring(html_source)
        jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')

        kg = ConjunctiveGraph()
        for json_ld_annots in jsonld_string :
            jsonld = json.loads(json_ld_annots)

            if '@context' in jsonld.keys():
                if ('//schema.org' in jsonld['@context']):
                    jsonld['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")

            print(f'{len(kg)} retrieved triples in KG')
            print(kg.serialize(format='turtle').decode())

        self.assertEqual(62, len(kg))


    def test_static_data_inra(self):
        #uri = 'https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/GANJ7J'
        uri = 'https://workflowhub.eu/workflows/45'
        #uri = 'https://bio.tools/jaspar'

        r = requests.get(uri)
        text = r.content
        #print(text.decode())
        #d = extruct.extract(html, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')
        d = extruct.extract(text, syntaxes=['microdata', 'json-ld'])
        #tree = html.fromstring(r.content)
        #print(tree.xpath('//script[@type="application/ld+json"]//text()'))
        #print(data)
        r.connection.close()

        print(d)
        kg = ConjunctiveGraph()

        for md in d['json-ld']:
            if '@context' in md.keys():
                print(md['@context'])
                if ('//schema.org' in md['@context']):
                    md['@context'] = '../static/data/jsonldcontext.json'
            #print(json.dumps(md, ensure_ascii=True, indent=True))
            kg.parse(data=json.dumps(md, ensure_ascii=True), format="json-ld")
        for md in d['microdata']:
            if '@context' in md.keys():
                if ('//schema.org' in md['@context']):
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        print(f'{len(kg)} retrieved triples in KG')
        print(kg.serialize(format='turtle').decode())
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
