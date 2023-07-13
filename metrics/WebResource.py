import time
from ssl import SSLError
from lxml import html
import logging
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import extruct
from pathlib import Path
from rdflib import ConjunctiveGraph, URIRef, Namespace
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
import json
import os
import re

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
    # WEB_BROWSER_HEADLESS.implicitly_wait(20)

    SERVER_TIMEOUT = 30

    status_code = None
    content_type = None
    mimetype = None
    browser_selenium = None
    html_selenium = None
    html_requests = None
    headers = None
    links_headers = None

    kg_var_strings = [
        "kg_links_header",
        "kg_auto",
        "kg_brut",
        "kg_links_html",
        "kg_html",
    ]

    # source: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-media-type-support.html
    RDF_MEDIA_TYPES_MAPPING = {
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

    def __init__(self, url, rdf_graph=None) -> None:
        self.id = "WebResource Unique ID for cache"
        self.url = url

        # TODO rename variable
        self.wr_dataset = ConjunctiveGraph()

        self.wr_dataset.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.wr_dataset.namespace_manager.bind("scs", URIRef("https://schema.org/"))
        self.wr_dataset.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        self.wr_dataset.namespace_manager.bind(
            "dct", URIRef("http://purl.org/dc/terms/")
        )

        self.init_kgs()

        if rdf_graph is None:
            response = requests.get(url)
            self.headers = response.headers
            self.status_code = response.status_code

            # mimetypes from headers
            mimetype = self.headers["Content-Type"].split(";")[0]
            self.mimetype = mimetype

            # list of possibles rdf formats from mimetypes
            rdf_formats = self.get_rdf_format_from_contenttype(mimetype)
            print(self.headers)

            cite_as, described_by, items = self.retrieve_links_from_headers()

            # get RDF from HTTP headers
            self.get_kg_from_header(described_by)

            # if not html, try to retrieve rdf from possible rdf format
            if mimetype != "text/html":
                response = self.request_from_url(self.url)

                # generate rdf graph from mapped mimetypes
                for rdf_format in rdf_formats:
                    print(rdf_format)
                    self.kg_auto = self.get_rdf_from_mimetype_match(
                        self.url, rdf_format, self.kg_auto
                    )

                # if no rdf found: brute force testing each RDF formats regardless of mimetypes
                if len(self.kg_auto) == 0:
                    for rdf_format in self.RDF_MEDIA_TYPES_MAPPING.keys():
                        self.kg_brut = self.get_rdf_from_mimetype_match(
                            url, rdf_format, self.kg_brut
                        )

                logging.info(
                    "Resource content_type is: " + self.headers["Content-Type"]
                )

            elif mimetype == "text/html":
                self.html_content = self.get_html_selenium(url)

                # should only use selenium here I think
                # TODO get RDF from HTTP html
                # response_request = self.request_from_url(self.url)
                # but need request for status_code
                # self.status_code = response_request.status_code
                # self.html_requests = response_request.content

                # if KG from HTTP link header == 0 look for link header in html
                if self.kg_links_header == 0:
                    links = self.retrieve_links_from_html(self.kg_html)

                    for link in links:
                        rel = link[0]
                        if rel == "describedby":
                            url = link[1]
                            link_mimetype = link[2]
                            rdf_formats = self.get_rdf_format_from_contenttype(
                                link_mimetype
                            )

                            for rdf_format in rdf_formats:
                                self.kg_links_html = self.get_rdf_from_mimetype_match(
                                    url, rdf_format, self.kg_links_html
                                )

                # get RDF metadata directly from html content
                self.html_to_rdf_extruct(self.html_content)

            # get static RDF metadata (already available in html sources)
            self.html_content = self.request_from_url(self.url)
            self.html_to_rdf_extruct(self.html_content)

            self.rdf = (
                self.kg_auto
                + self.kg_brut
                + self.kg_links_header
                + self.kg_links_html
                + self.kg_html
            )

            self.kg_auto.bind("wr", Namespace("http://webresource/"))
            # self.wr_dataset.add_graph(self.kg_auto)
            for s, p, o in self.kg_auto:
                self.wr_dataset.add((s, p, o, URIRef(self.url + "#mimetypes_match")))

            self.kg_brut.bind("wr", Namespace("http://webresource/"))
            # self.wr_dataset.add_graph(self.kg_brut)
            for s, p, o in self.kg_brut:
                self.wr_dataset.add((s, p, o, URIRef(self.url + "#rdfformats_match")))

            self.kg_links_header.bind("wr", Namespace("http://webresource/"))
            # self.wr_dataset.add_graph(self.kg_links_header)
            for s, p, o in self.kg_links_header:
                self.wr_dataset.add((s, p, o, URIRef(self.url + "#links_header")))

            self.kg_links_html.bind("wr", Namespace("http://webresource/"))
            # self.wr_dataset.add_graph(self.kg_links_html)
            for s, p, o in self.kg_links_html:
                self.wr_dataset.add((s, p, o, URIRef(self.url + "#links_html")))

            self.kg_html.bind("wr", Namespace("http://webresource/"))
            # self.wr_dataset.add_graph(self.kg_html)
            for s, p, o in self.kg_html:
                self.wr_dataset.add((s, p, o, URIRef(self.url + "#html")))

            # define the correct namespace for sc prefix
            # if self.is_schema_http(self.wr_dataset):
            #     self.wr_dataset.namespace_manager.bind("sc", URIRef("http://schema.org/"))
            # else:
            #     self.wr_dataset.namespace_manager.bind("sc", URIRef("https://schema.org/"))

            # replace all http with https for schema.org
            # self.wr_dataset.namespace_manager.bind("sc", URIRef("https://schema.org/"))
            # self.wr_dataset = self.schema_https_convert(self.wr_dataset)

            self.wr_dataset = clean_kg_excluding_ns_prefix(
                self.wr_dataset, "http://www.w3.org/1999/xhtml/vocab#"
            )

            print("HTML: " + str(len(self.kg_html)))
            print("LINKS HEADERS: " + str(len(self.kg_links_header)))
            print("AUTO: " + str(len(self.kg_auto)))
            print("FORMATS_GUESSING: " + str(len(self.kg_brut)))
            print("HTML LINKS: " + str(len(self.kg_links_html)))

        else:
            self.rdf = rdf_graph

        # self.rdf.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.rdf.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        self.rdf.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
        self.rdf = clean_kg_excluding_ns_prefix(
            self.rdf, "http://www.w3.org/1999/xhtml/vocab#"
        )

    def init_kgs(self):
        for var_str in self.kg_var_strings:
            setattr(
                WebResource,
                var_str,
                ConjunctiveGraph(identifier="http://webresource/" + var_str),
            )
            getattr(WebResource, var_str).namespace_manager.bind(
                "bsc", URIRef("https://bioschemas.org/")
            )
            getattr(WebResource, var_str).namespace_manager.bind(
                "dct", URIRef("http://purl.org/dc/terms/")
            )
            clean_kg_excluding_ns_prefix(
                getattr(WebResource, var_str), "http://www.w3.org/1999/xhtml/vocab#"
            )

    def get_kg_from_header(self, described_by):
        for link in described_by:
            reg_string = '<(.*?)>*;*rel="(.*?)"*;*type="(.*?)"'
            p = re.compile(reg_string)
            match = re.search(reg_string, link)
            url = match.group(1)
            rel = match.group(2)
            link_mimetype = match.group(3)

            rdf_formats = self.get_rdf_format_from_contenttype(link_mimetype)

            for rdf_format in rdf_formats:
                self.get_rdf_from_mimetype_match(url, rdf_format, self.kg_links_header)

    def get_url(self):
        return self.url

    def get_rdf(self):
        return self.wr_dataset

    def get_wr_kg_dataset(self):
        return self.wr_dataset

    def get_kg_auto(self):
        return self.kg_auto

    def get_kg_html(self):
        return self.kg_html

    def get_status_code(self):
        return self.status_code

    def get_html_requests(self):
        return self.html_requests

    def get_http_header(self):
        return self.headers

    @staticmethod
    def is_schema_http(kg):
        for s, p, o, g in kg.quads(None):
            if str(s).startswith("http://schema.org"):
                return True
            if str(p).startswith("http://schema.org"):
                return True
            if isinstance(o, URIRef):
                if str(o).startswith("http://schema.org"):
                    return True
        return False

    # Could be a static method
    def schema_https_convert(self, kg):
        for s, p, o, g in kg.quads(None):
            changed = False
            new_s = s
            if str(s).startswith("http://schema.org"):
                new_s = URIRef(str(s).replace("http", "https", 1))
                changed = True
            new_p = p
            if str(p).startswith("http://schema.org"):
                new_p = URIRef(str(p).replace("http", "https", 1))
                changed = True
            new_o = o
            if isinstance(o, URIRef):
                if str(o).startswith("http://schema.org"):
                    new_o = URIRef(str(o).replace("http", "https", 1))
                    changed = True
            if changed:
                kg.remove((s, p, o, g))
                kg.add((new_s, new_p, new_o, g))
        return kg

    def get_rdf_from_mimetype_match(self, url, rdf_format, kg):
        logging.debug("Getting RDF from: " + rdf_format)

        kg_temp = ConjunctiveGraph()
        response = requests.get(url)

        if response.status_code == 200:
            rdf_str = response.text
            try:
                # TODO check if merging works with ConjunctiveGraph using publicID (seems to keep only latest)
                kg_temp.parse(
                    data=rdf_str,
                    format=rdf_format,
                    publicID=url,
                )

                kg += kg_temp
                logging.debug(len(kg_temp))
            except Exception as err:
                # if error UnicodeDecodeError execute following code, otherwise continue to next format
                if type(err).__name__ == "BadSyntax":
                    print("RDF syntax error")
                    print(err)
                if type(err).__name__ == "UnicodeDecodeError":
                    print("UNICODE error")
                    print(err)
                    kg = self.handle_unicodedecodeerror(url, kg, response)

        return kg

    def get_rdf_format_from_contenttype(self, mimetype):
        all_mediatypes = [
            item
            for sublist in self.RDF_MEDIA_TYPES_MAPPING.values()
            for item in sublist
        ]
        rdf_formats = [
            i
            for i in self.RDF_MEDIA_TYPES_MAPPING
            if mimetype in self.RDF_MEDIA_TYPES_MAPPING[i]
        ]

        return rdf_formats

    def handle_unicodedecodeerror(self, url, kg, response):
        print("Handle JSON-LD parsing error")
        # base_path = Path(__file__).parent.parent  # current directory
        # static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())
        json_response = response.json()

        if "@context" in json_response.keys():
            if ("https://schema.org" in json_response["@context"]) or (
                "http://schema.org" in json_response["@context"]
            ):
                json_response["@context"] = self.static_file_path

        json_str = json.dumps(json_response, ensure_ascii=False)

        kg_temp = ConjunctiveGraph()

        kg_temp.parse(data=json_str, format="json-ld", publicID=url)
        for s, p, o in kg_temp:
            kg.add((s, p, o))

        return kg

    def retrieve_links_from_headers(self):
        links_col = []
        decsribed_by_col = []
        cite_as_col = []
        item_col = []
        headers = self.headers
        for k in headers.keys():
            if "link" in k.lower():
                l_header = headers[k]
                links = l_header.split(",")
                for link in links:
                    # print("----")
                    links_col.append(link)
                    tokens = link.split(";")
                    # print(tokens)
                    for t in tokens:
                        if 'rel="describedby"' in t:
                            decsribed_by_col.append(link)
                        elif 'rel="item"' in t:
                            item_col.append(link)
                        elif 'rel="cite-as"' in t:
                            cite_as_col.append(link)
        self.links_headers = (cite_as_col, decsribed_by_col, item_col)
        return cite_as_col, decsribed_by_col, item_col

    def retrieve_links_from_html(self, source_html):
        tree = html.fromstring(source_html)
        links = []

        txt = tree.xpath('//link[contains(@rel, "describedby")]')
        for t in txt:
            links.append(t.values())

        txt = tree.xpath('//link[contains(@rel, "cite-as")]')
        for t in txt:
            links.append(t.values())

        txt = tree.xpath('//link[contains(@rel, "item")]')
        for t in txt:
            links.append(t.values())
        return links

    # TODO Extruct can work with Selenium

    def request_from_url(self, url):
        nb_retry = 0
        while nb_retry < 3:
            try:
                nb_retry += 1
                response = requests.get(url=url, timeout=30, verify=False)
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

        return response.text

    def get_html_selenium(self, url):
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)
        time.sleep(2)
        browser.set_page_load_timeout(30)
        browser.implicitly_wait(30)

        WebDriverWait(self.WEB_BROWSER_HEADLESS, self.SERVER_TIMEOUT).until(
            lambda wd: self.WEB_BROWSER_HEADLESS.execute_script(
                "return document.readyState"
            )
            == "complete",
            "Page taking too long to load",
        )
        html_content = browser.page_source
        logging.debug(type(browser.page_source))
        logging.info(f"size of the parsed web page: {len(html_content)}")
        return html_content

    # @staticmethod
    def html_to_rdf_extruct(self, html_source) -> ConjunctiveGraph:
        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )

        kg_jsonld = ConjunctiveGraph()

        if "json-ld" in data.keys():
            for md in data["json-ld"]:
                kg_jsonld.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )

        kg_rdfa = ConjunctiveGraph()

        if "rdfa" in data.keys():
            for md in data["rdfa"]:
                kg_rdfa.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )
                print(len(kg_rdfa))

        kg_microdata = ConjunctiveGraph()

        if "microdata" in data.keys():
            for md in data["microdata"]:
                kg_microdata.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )
                print(len(kg_microdata))

        kg_extruct = kg_jsonld + kg_rdfa + kg_microdata

        for s, p, o in kg_extruct:
            self.kg_html.add((s, p, o))

    def __str__(self) -> str:
        out = """Web resource under FAIR assesment:\n\t"""
        out += self.url + "\n\t"
        out += str(len(self.rdf)) + " embedded RDF triples"
        return out
