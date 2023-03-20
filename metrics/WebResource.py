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
from rdflib import ConjunctiveGraph, URIRef
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
import json
import os
from json.decoder import JSONDecodeError

from metrics.util import clean_kg_excluding_ns_prefix

logger = logging.getLogger("DEV")


class WebResource:
    prefs = {
        "download_restrictions": 3,
        "download.prompt_for_download": False,
        "download.default_directory": "NUL",
    }

    base_path = Path(__file__).parent.parent  # current directory

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")

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
            # get static RDF metadata (already available in html sources)
            kg_1 = self.extract_rdf_extruct(self.url)
            if self.content_type:
                if ("html" in self.content_type) or ("ld+json" in self.content_type):
                    logging.info("Resource content_type is HTML")
                    # get dynamic RDF metadata (generated from JS)
                    kg_2 = WebResource.extract_rdf_selenium(self.url)
                    self.rdf = kg_1 + kg_2
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

    # TODO Extruct can work with Selenium

    def retrieve_html_selenium(self):
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(self.url)
        self.html_selenium = browser.page_source
        self.browser_selenium = browser

    def retrieve_html_request(self):
        nb_retry = 0
        while nb_retry < 3:
            try:
                nb_retry += 1
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

    # @staticmethod
    def extract_rdf_extruct(self, url) -> ConjunctiveGraph:
        nb_retry = 0
        response = None
        while nb_retry < 3:
            try:
                nb_retry += 1
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

        if not response:
            logger.error(f"Could not get HTML doc from {url}")
            return ConjunctiveGraph()

        self.status_code = response.status_code
        self.content_type = response.headers["Content-Type"]
        html_source = response.content

        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )

        kg_jsonld = ConjunctiveGraph()

        # kg = ConjunctiveGraph()

        if "json-ld" in data.keys():
            for md in data["json-ld"]:

                try:
                    kg_jsonld.parse(
                        data=md,
                        format="json-ld",
                        publicID=url,
                    )
                except UnicodeDecodeError as unicode_error:
                    logger.error(
                        f"Cannot parse RDF from {url} due to UnicodeDecodeError"
                    )
                    logger.error(unicode_error)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Cannot parse RDF from {url} due to JSONDecodeError")
                    logger.error(json_error)

        kg_rdfa = ConjunctiveGraph()

        if "rdfa" in data.keys():
            for md in data["rdfa"]:

                try:
                    kg_rdfa.parse(
                        data=json.dumps(md, ensure_ascii=False),
                        format="json-ld",
                        publicID=url,
                    )
                except UnicodeDecodeError as unicode_error:
                    logger.error(
                        f"Cannot parse RDF from {url} due to UnicodeDecodeError"
                    )
                    logger.error(unicode_error)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Cannot parse RDF from {url} due to JSONDecodeError")
                    logger.error(json_error)

        kg_microdata = ConjunctiveGraph()

        if "microdata" in data.keys():
            for md in data["microdata"]:

                try:
                    kg_microdata.parse(
                        data=json.dumps(md, ensure_ascii=False),
                        format="json-ld",
                        publicID=url,
                    )
                except UnicodeDecodeError as unicode_error:
                    logger.error(
                        f"Cannot parse RDF from {url} due to UnicodeDecodeError"
                    )
                    logger.error(unicode_error)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Cannot parse RDF from {url} due to JSONDecodeError")
                    logger.error(json_error)

        kg_extruct = kg_jsonld + kg_rdfa + kg_microdata

        logging.debug(kg_extruct.serialize(format="turtle"))

        kg_extruct.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg_extruct.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg_extruct.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        # print(len(kg_extruct))
        return kg_extruct

    @staticmethod
    def extract_rdf_selenium(url) -> ConjunctiveGraph:
        kg = ConjunctiveGraph()

        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)
        # browser.quit()
        logging.debug(type(browser.page_source))
        logging.debug(f"size of the parsed web page: {len(browser.page_source)}")

        try:
            element = browser.find_element_by_xpath(
                "//script[@type='application/ld+json']"
            )
            element = element.get_attribute("outerHTML")
            # browser.quit()

            tree = html.fromstring(element)
            jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')

            for json_ld_annots in jsonld_string:
                jsonld = {}
                try:
                    jsonld = json.loads(json_ld_annots)
                except JSONDecodeError as err:
                    print(err)
                    continue

                if jsonld is None:
                    continue

                try:
                    kg.parse(
                        data=json.dumps(jsonld, ensure_ascii=False),
                        format="json-ld",
                        publicID=url,
                    )
                except UnicodeDecodeError as unicode_error:
                    print(f"Cannot parse RDF from {url} due to UnicodeDecodeError")
                    logger.error(
                        f"Cannot parse RDF from {url} due to UnicodeDecodeError"
                    )
                    logger.error(unicode_error)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Cannot parse RDF from {url} due to JSONDecodeError")
                    logger.error(json_error)
                logging.debug(f"{len(kg)} retrieved triples in KG")
                # logging.debug(kg.serialize(format="turtle"))

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
        out += str(len(self.rdf)) + " embedded RDF triples"
        return out
