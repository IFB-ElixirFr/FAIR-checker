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
import rdflib
from rdflib import ConjunctiveGraph, URIRef
import requests
import json
import os

from metrics.util import clean_kg_excluding_ns_prefix


class WebResource:
    prefs = {
        "download_restrictions": 3,
        "download.prompt_for_download": False,
        "download.default_directory": "NUL",
    }

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_experimental_option(
    #     "prefs", prefs
    # )
    proxy = os.getenv("HTTP_PROXY")
    if proxy:
        chrome_options.add_argument("--proxy-server=" + proxy)

    WEB_BROWSER_HEADLESS = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options
    )
    WEB_BROWSER_HEADLESS.implicitly_wait(20)

    status_code = None
    content_type = None
    browser_selenium = None
    html_selenium = None
    html_requests = None

    def __init__(self, url, rdf_graph=None) -> None:
        self.id = "WebResource Unique ID for cache"
        self.url = url

        if rdf_graph is None:

            headers = self.get_http_header(url)
            mimetype = headers["Content-Type"].split(";")[0]
            rdf_formats = self.get_rdf_format_from_contenttype(mimetype)

            kg_auto = ConjunctiveGraph()
            for rdf_format in rdf_formats:
                response = requests.get(url)
                if response.status_code == 200:
                    try:
                        rdf_str = response.text
                        kg_auto.parse(data=rdf_str, format=rdf_format)
                    except rdflib.exceptions.ParserError:
                        pass
            print("AUTO: " + str(len(kg_auto)))

            logging.info("Resource content_type is: " + headers["Content-Type"])
            # get static RDF metadata (already available in html sources)
            # kg_1 = self.extract_rdf_extruct(self.url)

            if "text/html" in headers["Content-Type"]:
                kg_1 = self.extract_rdf_extruct(self.url)
                # get dynamic RDF metadata (generated from JS)
                kg_2 = WebResource.extract_rdf_selenium(self.url)
                self.rdf = kg_1 + kg_2
            elif "application/json" in headers["Content-Type"]:

                base_path = Path(__file__).parent.parent  # current directory
                static_file_path = str(
                    (base_path / "static/data/jsonldcontext.json").resolve()
                )

                response = requests.get(url)
                if response.status_code == 200:
                    json_response = response.json()

                    if "@context" in json_response.keys():
                        if ("https://schema.org" in json_response["@context"]) or (
                            "http://schema.org" in json_response["@context"]
                        ):
                            json_response["@context"] = static_file_path

                    json_str = json.dumps(json_response, ensure_ascii=False)

                    kg = ConjunctiveGraph()
                    kg.parse(data=json_str, format="json-ld")
                    print(len(kg))
                    self.rdf = kg

            elif "text/turtle" in headers["Content-Type"]:

                response = requests.get(url)
                turtle_str = response.text
                if response.status_code == 200:
                    kg = ConjunctiveGraph()
                    kg.parse(data=turtle_str, format="turtle")
                    print(len(kg))
                    self.rdf = kg

            elif "text/n3" in headers["Content-Type"]:
                response = requests.get(url)
                n3_str = response.text
                if response.status_code == 200:
                    kg = ConjunctiveGraph()
                    kg.parse(data=n3_str, format="n3")
                    print(len(kg))
                    self.rdf = kg

            elif "application/xml" in headers["Content-Type"]:
                response = requests.get(url)
                xml_str = response.text
                if response.status_code == 200:
                    kg = ConjunctiveGraph()
                    kg.parse(data=xml_str, format="xml")
                    print(len(kg))
                    self.rdf = kg

            else:
                self.rdf = kg_1
        else:
            self.rdf = rdf_graph

        self.rdf.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.rdf.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        self.rdf.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
        self.rdf = clean_kg_excluding_ns_prefix(
            self.rdf, "http://www.w3.org/1999/xhtml/vocab#"
        )

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

    def get_http_header(self, url):
        response = requests.head(url)
        print(
            "#########################\n#########################\n#########################\n"
        )
        print(response.headers)
        content_type = response.headers["Content-Type"]
        print(content_type)
        return response.headers

    def get_rdf_format_from_contenttype(self, mimetype):
        # source: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-media-type-support.html
        rdf_media_types_mapping = {
            "turtle": ["text/turtle"],
            "xml": ["application/rdf+xml"],
            "json-ld": ["application/ld+json"],
            "ntriples": [
                "application/n-triples",
                "text/turtle",
                "text/plain",
            ],
            "n3": ["text/n3"],
            "trig": [
                "application/trig",
            ],
            "trix": [
                "application/trix",
            ],
            "nquads": ["application/n-quads", "text/x-nquads"],
        }
        all_mediatypes = [
            item for sublist in rdf_media_types_mapping.values() for item in sublist
        ]
        rdf_formats = [
            i for i in rdf_media_types_mapping if mimetype in rdf_media_types_mapping[i]
        ]

        return rdf_formats

    # TODO Extruct can work with Selenium

    def retrieve_html_selenium(self):
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(self.url)
        self.html_selenium = browser.page_source
        self.browser_selenium = browser

    def retrieve_html_request(self):
        while True:
            try:
                response = requests.get(url=self.url, timeout=10, verify=False)
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
    def html_to_rdf_extruct(html_source) -> ConjunctiveGraph:
        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )
        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  # current directory
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

        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        return kg

    # @staticmethod
    def extract_rdf_extruct(self, url) -> ConjunctiveGraph:
        while True:
            try:
                response = requests.get(url=url, timeout=10, verify=False)
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
        self.content_type = response.headers["Content-Type"]
        html_source = response.content

        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )

        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        if "json-ld" in data.keys():
            for md in data["json-ld"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = static_file_path
                kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        if "rdfa" in data.keys():
            for md in data["rdfa"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = static_file_path
                kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        if "microdata" in data.keys():
            for md in data["microdata"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = static_file_path
                kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        logging.debug(kg.serialize(format="turtle"))

        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        return kg

    @staticmethod
    def extract_rdf_selenium(url) -> ConjunctiveGraph:
        kg = ConjunctiveGraph()

        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)
        # self.html_source = browser.page_source
        # browser.quit()
        logging.debug(type(browser.page_source))
        logging.info(f"size of the parsed web page: {len(browser.page_source)}")

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
                print(type(jsonld))
                print(jsonld)
                if type(jsonld) == list:
                    jsonld = jsonld[0]
                if "@context" in jsonld.keys():
                    if "//schema.org" in jsonld["@context"]:
                        jsonld["@context"] = static_file_path
                kg.parse(data=json.dumps(jsonld, ensure_ascii=False), format="json-ld")
                logging.debug(f"{len(kg)} retrieved triples in KG")
                logging.debug(kg.serialize(format="turtle"))

        except NoSuchElementException:
            logging.warning('Can\'t find "application/ld+json" content')
            pass

        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        return kg

    def __str__(self) -> str:
        out = """Web resource under FAIR assesment:\n\t"""
        out += self.url + "\n\t"
        out += len(self.rdf) + " embedded RDF triples"
        return out
