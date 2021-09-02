from lxml import html
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from rdflib import ConjunctiveGraph
import json


class WebResource:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    WEB_BROWSER_HEADLESS = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options
    )
    WEB_BROWSER_HEADLESS.implicitly_wait(20)

    @staticmethod
    def extract_rdf_selenium(url) -> ConjunctiveGraph:
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)

        # self.html_source = browser.page_source
        # browser.quit()
        logging.debug(type(browser.page_source))

        # html_source = browser.page_source
        # element = browser.find_element_by_xpath('//*')
        element = browser.find_element_by_xpath("//script[@type='application/ld+json']")
        element = element.get_attribute("outerHTML")
        print(element)

        # browser.quit()

        # tree = html.fromstring(html_source)
        tree = html.fromstring(element)
        jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')

        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        kg = ConjunctiveGraph()
        for json_ld_annots in jsonld_string:
            jsonld = json.loads(json_ld_annots)
            if "@context" in jsonld.keys():
                if "//schema.org" in jsonld["@context"]:
                    jsonld["@context"] = static_file_path
            kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")
            logging.debug(f"{len(kg)} retrieved triples in KG")
            logging.debug(kg.serialize(format="turtle").decode())
        return kg

    def __init__(self, url) -> None:
        self.url = url
        kg = WebResource.extract_rdf_selenium(self.url)
        # self.html_source = source
        self.rdf = kg

    def __str__(self) -> str:
        out = f"Web resource under FAIR assesment:\n\t- {self.url} \n\t- {len(self.rdf)} embedded RDF triples"
        return out
