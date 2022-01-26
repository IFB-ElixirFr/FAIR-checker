import time
from ssl import SSLError
from lxml import html
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import extruct
from pathlib import Path
from rdflib import ConjunctiveGraph
import requests
import json


class WebResource:
    print("in webresouirce")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    WEB_BROWSER_HEADLESS = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options
    )
    WEB_BROWSER_HEADLESS.implicitly_wait(20)

    status_code = None
    browser_selenium = None
    html_selenium = None
    html_requests = None

    def __init__(self, url) -> None:
        self.url = url
        self.id = "WebResource Unique ID for cache"
        # get dynamic RDF metadata (generated from JS)
        kg_1 = WebResource.extract_rdf_selenium(self.url)
        # get static RDF metadata (already available in html sources)
        kg_2 = self.extract_rdf_extruct(self.url)
        self.rdf = kg_1 + kg_2

    def get_url(self):
        return self.url

    def get_rdf(self):
        return self.rdf

    def get_status_code(self):
        return self.status_code

    def get_html_selenium(self):
        return self.html_selenium

    def get_html_requests(self):
        return self.html_requests

    # TODO Extruct can work with Selenium

    def retrieve_html_selenium(self):
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(self.url)
        self.html_selenium = browser.page_source
        self.browser_selenium = browser

    def retrieve_html_request(self):
        while True:
            try:
                response = requests.get(url=self.url, timeout=10)
                break
            except SSLError:
                time.sleep(5)
            except requests.exceptions.Timeout:
                print("Timeout, retrying")
                time.sleep(5)
            except requests.exceptions.ConnectionError as e:
                print(e)
                print("ConnectionError, retrying...")
                time.sleep(10)

        self.status_code = response.status_code
        self.html_requests = response.content

    @staticmethod
    def html_to_rdf_extruct(html_source):
        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )
        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  ## current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        for md in data["json-ld"]:
            if "@context" in md.keys():
                print(md["@context"])
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data["rdfa"]:
            if "@context" in md.keys():
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data["microdata"]:
            if "@context" in md.keys():
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        logging.debug(kg.serialize(format="turtle"))
        return kg

    # @staticmethod
    def html_to_rdf_parse_ld(self, html_source):
        kg = ConjunctiveGraph()
        browser = self.browser_selenium
        logging.debug(type(browser.page_source))

        try:
            element = browser.find_element_by_xpath(
                "//script[@type='application/ld+json']"
            )
            element = element.get_attribute("outerHTML")
            # browser.quit()

            tree = html.fromstring(element)
            jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')
            # try:
            # jsonld_string = html.fromstring(html_source).xpath('//script[@type="application/ld+json"]//text()')
            print(jsonld_string)
            base_path = Path(__file__).parent.parent  # current directory
            static_file_path = str(
                (base_path / "static/data/jsonldcontext.json").resolve()
            )

            for json_ld_annots in jsonld_string:
                jsonld = json.loads(json_ld_annots)
                if "@context" in jsonld.keys():
                    if "//schema.org" in jsonld["@context"]:
                        jsonld["@context"] = static_file_path
                kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")
                logging.debug(f"{len(kg)} retrieved triples in KG")
                logging.debug(kg.serialize(format="turtle"))

        except NoSuchElementException:
            logging.warning('Can\'t find "application/ld+json" content')
            pass

        return kg

    # @staticmethod
    def extract_rdf_extruct(self, url) -> ConjunctiveGraph:
        while True:
            try:
                response = requests.get(url=url, timeout=10)
                break
            except SSLError:
                time.sleep(5)
            except requests.exceptions.Timeout:
                print("Timeout, retrying")
                time.sleep(5)
            except requests.exceptions.ConnectionError as e:
                print(e)
                print("ConnectionError, retrying...")
                time.sleep(10)

        self.status_code = response.status_code
        html_source = response.content

        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )
        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  ## current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        for md in data["json-ld"]:
            if "@context" in md.keys():
                print(md["@context"])
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data["rdfa"]:
            if "@context" in md.keys():
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data["microdata"]:
            if "@context" in md.keys():
                if ("https://schema.org" in md["@context"]) or (
                    "http://schema.org" in md["@context"]
                ):
                    md["@context"] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        logging.debug(kg.serialize(format="turtle"))
        return kg

    @staticmethod
    def extract_rdf_selenium(url) -> ConjunctiveGraph:
        kg = ConjunctiveGraph()

        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)
        # self.html_source = browser.page_source
        # browser.quit()
        logging.debug(type(browser.page_source))
        print(len(browser.page_source))

        try:
            element = browser.find_element_by_xpath(
                "//script[@type='application/ld+json']"
            )
            element = element.get_attribute("outerHTML")
            # browser.quit()

            tree = html.fromstring(element)
            jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')

            base_path = Path(__file__).parent.parent  # current directory
            static_file_path = str(
                (base_path / "static/data/jsonldcontext.json").resolve()
            )

            for json_ld_annots in jsonld_string:
                jsonld = json.loads(json_ld_annots)
                if "@context" in jsonld.keys():
                    if "//schema.org" in jsonld["@context"]:
                        jsonld["@context"] = static_file_path
                kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")
                logging.debug(f"{len(kg)} retrieved triples in KG")
                logging.debug(kg.serialize(format="turtle"))

        except NoSuchElementException:
            logging.warning('Can\'t find "application/ld+json" content')
            pass

        return kg

    def __str__(self) -> str:
        out = f"Web resource under FAIR assesment:\n\t- {self.url} \n\t- {len(self.rdf)} embedded RDF triples"
        return out
