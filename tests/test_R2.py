import unittest
from lxml import html
import requests
import json
from pathlib import Path
from rdflib import ConjunctiveGraph
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import extruct

from metrics.R_1_2_Impl import R_1_2_Impl


###
### TODO check this issue https://github.com/RDFLib/rdflib-jsonld/issues/84
###
class R2ImplTestCase(unittest.TestCase):
    # def setUp(self):

    uri_test = "https://workflowhub.eu/workflows/45"

    def test_extract_html_requests(self):
        class_r2 = R_1_2_Impl(self.uri_test)
        class_r2.set_url(self.uri_test)
        class_r2.extract_html_requests()
        requests_status_code = class_r2.get_requests_status_code()
        self.assertEqual(200, requests_status_code)

    def test_extract_rdf(self):
        class_r2 = R_1_2_Impl(self.uri_test)
        class_r2.set_url(self.uri_test)
        class_r2.extract_html_requests()
        class_r2.extract_rdf()
        self.assertEqual(103, len(class_r2.get_jsonld()))

    def test_R2_Impl(self):
        class_r2 = R_1_2_Impl(self.uri_test)
        print(class_r2.get_name())
        uri = "https://workflowhub.eu/workflows/45"
        # uri = "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/A4KXE7"
        class_r2.set_url(uri)
        class_r2.extract_html_requests()
        # class_r2.extract_html_selenium()
        # print(class_r2.get_html_source())
        class_r2.extract_rdf()
        print("Classes:")
        for rdf_class in class_r2.get_classes():
            print(str(rdf_class[0]))

        print("\nProperties:")
        for rdf_prop in class_r2.get_properties():
            print(str(rdf_prop[0]))
            print(class_r2.ask_LOV(rdf_prop[0]))
            # for obj in class_r2.get_jsonld().objects(predicate=rdf_prop[0]):
            # print(obj)
            # if class_r2.is_valid_uri(obj):
            #     print(class_r2.ask_LOV(obj))

        # for s, p, o in class_r2.get_jsonld():
        #     print("%s : %s : %s" % (s,p,o))

    def test_dynamic_biotools(self):
        # uri = 'https://workflowhub.eu/workflows/45'
        uri = "http://bio.tools/jaspar"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # browser = webdriver.Chrome(options = chrome_options)
        browser = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options
        )
        browser.implicitly_wait(10)
        browser.get(uri)

        # html_source = browser.page_source
        # element = browser.find_element_by_xpath('//*')
        element = browser.find_element_by_xpath("//script[@type='application/ld+json']")
        print(element)
        element = element.get_attribute("outerHTML")
        print(element)

        browser.quit()

        # tree = html.fromstring(html_source)
        tree = html.fromstring(element)
        jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')

        base_path = Path(__file__).parent.parent  ## current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        kg = ConjunctiveGraph()
        for json_ld_annots in jsonld_string:
            jsonld = json.loads(json_ld_annots)

            if "@context" in jsonld.keys():
                if "//schema.org" in jsonld["@context"]:
                    jsonld["@context"] = static_file_path
            kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")

            print(f"{len(kg)} retrieved triples in KG")
            print(kg.serialize(format="turtle").decode())

        self.assertEqual(61, len(kg))

    def test_static_data_inra(self):
        # uri = 'https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/GANJ7J'
        uri = "https://workflowhub.eu/workflows/45"
        # uri = 'https://bio.tools/jaspar'

        r = requests.get(uri)
        text = r.content
        # print(text.decode())
        # d = extruct.extract(html, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')
        d = extruct.extract(text, syntaxes=["microdata", "json-ld"])
        # tree = html.fromstring(r.content)
        # print(tree.xpath('//script[@type="application/ld+json"]//text()'))
        # print(data)
        r.connection.close()

        print(d)
        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  ## current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        for md in d["json-ld"]:
            if "@context" in md.keys():
                print(md["@context"])
                if "//schema.org" in md["@context"]:
                    md["@context"] = static_file_path
            # print(json.dumps(md, ensure_ascii=True, indent=True))
            kg.parse(data=json.dumps(md, ensure_ascii=True), format="json-ld")
        for md in d["microdata"]:
            if "@context" in md.keys():
                if "//schema.org" in md["@context"]:
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        print(f"{len(kg)} retrieved triples in KG")
        print(kg.serialize(format="turtle").decode())
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
