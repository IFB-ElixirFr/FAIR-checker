import time
from ssl import SSLError
from lxml import html
import logging
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import extruct
from pathlib import Path
import rdflib
from rdflib import ConjunctiveGraph, URIRef, Dataset, Namespace
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
import json
import os
import re

from pyparsing import (
    Word,
    alphas,
    alphanums,
    Group,
    Combine,
    Forward,
    ZeroOrMore,
    Optional,
    oneOf,
    QuotedString,
    Suppress,
)
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from metrics.util import clean_kg_excluding_ns_prefix


class WebResource:
    prefs = {
        "download_restrictions": 3,
        "download.prompt_for_download": False,
        "download.default_directory": "NUL",
    }

    base_path = Path(__file__).parent.parent  # current directory
    static_file_path = "file://" + str(
        (base_path / "static/data/jsonldcontext.json").resolve()
    )

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
        "kg_html"
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

        self.wr_dataset = Dataset()
        
        # self.kg_links_header = ConjunctiveGraph(identifier="http://webresource/links_headers")
        # self.kg_auto = ConjunctiveGraph(identifier="http://webresource/auto")
        # self.kg_brut = ConjunctiveGraph(identifier="http://webresource/brut")
        # self.kg_links_html = ConjunctiveGraph(identifier="http://webresource/links_html")
        # self.kg_html = ConjunctiveGraph(identifier="http://webresource/html")

        self.init_kgs()
        
        # b = [self.get_var_name(el) for el in kg_list]
        # print(b)



        if rdf_graph is None:

            # get headers of the resource
            response = requests.head(url)
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
                    self.kg_auto = self.get_rdf_from_mimetype_match(self.url, rdf_format, self.kg_auto)

                # if no rdf found: brutforce testing each RDF formats regardless of mimetypes
                if len(self.kg_auto) == 0:
                    rdf_str = response.text
                    for rdf_format in self.RDF_MEDIA_TYPES_MAPPING.keys():
                        self.kg_brut = self.get_rdf_from_mimetype_match(url, rdf_format, self.kg_brut)

                logging.info(
                    "Resource content_type is: " + self.headers["Content-Type"]
                )

            elif mimetype == "text/html":

                self.html_content = self.get_html_selenium(url)
                # print(len(self.extract_rdf_selenium(url)))

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
                                kg_links_html = self.get_rdf_from_mimetype_match(
                                    url, rdf_format, kg_links_html
                                )

                # get RDF metadata directly from html content
                self.html_to_rdf_extruct(self.html_content)

                # self.kg_selenium = kg_selenium

                # self.rdf = kg_requests + kg_selenium
                # self.html_rdf = kg_requests + kg_selenium

                # print("EXTRUCT: " + str(len(kg_requests)))
                # print("SELENIUM: " + str(len(kg_selenium)))
                # print("HTML: " + str(len(self.kg_html)))

            else:
                # get static RDF metadata (already available in html sources)
                self.html_content = self.request_from_url(self.url)
                self.html_to_rdf_extruct(self.html_content)

                


            self.rdf = (
                # self.kg_requests
                # + self.kg_selenium
                self.kg_auto
                + self.kg_brut
                + self.kg_links_header
                + self.kg_links_html
                + self.kg_html
            )

            self.kg_auto.bind("wr", Namespace("http://webresource/"))
            self.wr_dataset.add_graph(self.kg_auto)

            self.kg_brut.bind("wr", Namespace("http://webresource/"))
            self.wr_dataset.add_graph(self.kg_brut)

            self.kg_links_header.bind("wr", Namespace("http://webresource/"))
            self.wr_dataset.add_graph(self.kg_links_header)

            self.kg_links_html.bind("wr", Namespace("http://webresource/"))
            self.wr_dataset.add_graph(self.kg_links_html)

            self.kg_html.bind("wr", Namespace("http://webresource/"))
            self.wr_dataset.add_graph(self.kg_html)

            # self.wr_dataset.bind("sc", Namespace("http://schema.org/"))
            # self.wr_dataset.namespace_manager.bind("sc", URIRef("http://schema.org/"))
            # self.wr_dataset.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
            # self.wr_dataset.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
            self.wr_dataset = clean_kg_excluding_ns_prefix(
                self.wr_dataset, "http://www.w3.org/1999/xhtml/vocab#"
            )
            # self.wr_dataset.add_graph(self.kg_auto)
            # print("######################")
            # for namespace in self.kg_links_header.namespaces():
            #     print(namespace)
            # print(self.rdf.serialize(format="trig"))
            print("HTML: " + str(len(self.kg_html)))
            print("LINKS HEADERS: " + str(len(self.kg_links_header)))
            print("AUTO: " + str(len(self.kg_auto)))
            print("BRUTFORCE: " + str(len(self.kg_brut)))
            print("LINKS HTML: " + str(len(self.kg_links_html)))

            for kg in self.get_wr_kg_dataset().graphs():
                print(len(kg))

        else:
            self.rdf = rdf_graph

        self.rdf.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.rdf.namespace_manager.bind("namespacebsc", URIRef("https://bioschemas.org/"))
        self.rdf.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
        self.rdf = clean_kg_excluding_ns_prefix(
            self.rdf, "http://www.w3.org/1999/xhtml/vocab#"
        )
        # print("Full graph size: " + str(len(self.rdf)))
        # print(self.rdf.serialize(format="json-ld"))

    def init_kgs(self):
        for var_str in self.kg_var_strings:
            # print(var_str)

            setattr(WebResource, var_str, ConjunctiveGraph(identifier="http://webresource/" + var_str))


            clean_kg_excluding_ns_prefix(
                getattr(WebResource, var_str), "http://schema.org/"
            )
            getattr(WebResource, var_str).namespace_manager.bind("sc", URIRef("http://schema.org/"))
            getattr(WebResource, var_str).namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
            getattr(WebResource, var_str).namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
            # getattr(WebResource, var_str).bind("sc", Namespace("http://schema.org/"))
            clean_kg_excluding_ns_prefix(
                getattr(WebResource, var_str), "http://www.w3.org/1999/xhtml/vocab#"
            )

        # print(self.kg_links_header.namespaces())
        # for namespace in self.kg_links_header.namespaces():
        #     print(namespace)


        # self.kg_links_header.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        # self.kg_links_header.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        # self.kg_links_header.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))


    # def get_var_name(variable):
    #     for name, value in globals().items():
    #         if value is variable:
    #             return name


    def get_kg_from_header(self, described_by):
        # get RDF from HTTP headers
        # kg_links_header = self.kg_links_header
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


    # def get_kg_from_rdf_formats(self, format):
    #     print("toto")

    def get_url(self):
        return self.url

    def get_rdf(self):
        return self.rdf

    def get_wr_kg_dataset(self):
        return self.wr_dataset

    def get_kg_auto(self):
        return self.kg_auto

    def get_kg_html(self):
        return self.kg_html

    def get_status_code(self):
        return self.status_code

    # def get_html_selenium(self):
    #     return self.html_selenium

    def get_html_requests(self):
        return self.html_requests

    def get_http_header(self):
        return self.headers

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
                for s, p, o in kg_temp:
                    kg.add((s, p, o))
                # print("######################")
                # for namespace in kg.namespaces():
                #     print(namespace)   
            except Exception as err:
                # if error UnicodeDecodeError execute following code, otherwise continue to next format
                if type(err).__name__ == "UnicodeDecodeError":
                    print(err)
                    print("ERROR UNICODE")
                    kg = self.handle_unicodedecodeerror(url, kg, response)
        print(len(kg))

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
        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())
        json_response = response.json()

        if "@context" in json_response.keys():
            if ("https://schema.org" in json_response["@context"]) or (
                "http://schema.org" in json_response["@context"]
            ):
                json_response["@context"] = self.static_file_path

            # if ("https://schema.org" in json_response["@context"]) or (
            #     "http://schema.org" in json_response["@context"]
            # ):
            #     json_response["@context"] = self.static_file_path

        # kg.parse(
        #     data=json.dumps(json_response, ensure_ascii=False),
        #     format="json-ld",
        #     publicID=self.url,
        # )

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

        # self.html_requests = response.content
        return response

    def get_html_selenium(self, url):

        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)

        WebDriverWait(self.WEB_BROWSER_HEADLESS, self.SERVER_TIMEOUT).until(
            lambda wd: self.WEB_BROWSER_HEADLESS.execute_script("return document.readyState") == 'complete',
            "Page taking too long to load"
        )
        html_content = browser.page_source
        logging.debug(type(browser.page_source))
        logging.info(f"size of the parsed web page: {len(browser.page_source)}")
        # print(browser.page_source)
        return browser.page_source

    # @staticmethod
    def html_to_rdf_extruct(self, html_source) -> ConjunctiveGraph:
        data = extruct.extract(
            html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
        )

        kg_jsonld = ConjunctiveGraph()

        if "json-ld" in data.keys():
            for md in data["json-ld"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = self.static_file_path
                kg_jsonld.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )

        kg_rdfa = ConjunctiveGraph()

        if "rdfa" in data.keys():
            for md in data["rdfa"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = self.static_file_path
                kg_rdfa.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )

        kg_microdata = ConjunctiveGraph()

        if "microdata" in data.keys():
            for md in data["microdata"]:
                if "@context" in md.keys():
                    if ("https://schema.org" in md["@context"]) or (
                        "http://schema.org" in md["@context"]
                    ):
                        md["@context"] = self.static_file_path
                kg_microdata.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )

        kg_extruct = kg_jsonld + kg_rdfa + kg_microdata

        # logging.debug(kg_extruct.serialize(format="turtle"))


        for s, p, o in kg_extruct:
            self.kg_html.add((s, p, o))

        # self.kg_html.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        # self.kg_html.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        # self.kg_html.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        # self.kg_links_header.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        # self.kg_links_header.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        # self.kg_links_header.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        # self.kg_html = kg_extruct

        # return kg_extruct

    # # @staticmethod
    # def extract_rdf_extruct(self, url) -> ConjunctiveGraph:
    #     while True:
    #         try:
    #             response = requests.get(url=url, timeout=10, verify=False)
    #             break
    #         except SSLError:
    #             time.sleep(5)
    #         except requests.exceptions.Timeout:
    #             print("Timeout, retrying")
    #             time.sleep(5)
    #         except requests.exceptions.ConnectionError as e:
    #             print(e)
    #             print("ConnectionError, retrying...")
    #             time.sleep(10)

    #     self.status_code = response.status_code
    #     self.content_type = response.headers["Content-Type"]
    #     html_source = response.content

    #     data = extruct.extract(
    #         html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
    #     )

    #     kg = ConjunctiveGraph()

    #     if "json-ld" in data.keys():
    #         for md in data["json-ld"]:
    #             if "@context" in md.keys():
    #                 if ("https://schema.org" in md["@context"]) or (
    #                     "http://schema.org" in md["@context"]
    #                 ):
    #                     md["@context"] = self.static_file_path
    #             kg.parse(
    #                 data=json.dumps(md, ensure_ascii=False),
    #                 format="json-ld",
    #                 publicID=url,
    #             )
    #     if "rdfa" in data.keys():
    #         for md in data["rdfa"]:
    #             if "@context" in md.keys():
    #                 if ("https://schema.org" in md["@context"]) or (
    #                     "http://schema.org" in md["@context"]
    #                 ):
    #                     md["@context"] = self.static_file_path
    #             kg.parse(
    #                 data=json.dumps(md, ensure_ascii=False),
    #                 format="json-ld",
    #                 publicID=url,
    #             )

    #     if "microdata" in data.keys():
    #         for md in data["microdata"]:
    #             if "@context" in md.keys():
    #                 if ("https://schema.org" in md["@context"]) or (
    #                     "http://schema.org" in md["@context"]
    #                 ):
    #                     md["@context"] = self.static_file_path
    #             kg.parse(
    #                 data=json.dumps(md, ensure_ascii=False),
    #                 format="json-ld",
    #                 publicID=url,
    #             )

    #     # logging.debug(kg.serialize(format="turtle"))

    #     kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
    #     kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
    #     kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

    #     return kg

    # @staticmethod
    # def extract_rdf_selenium(url) -> ConjunctiveGraph:
    #     kg = ConjunctiveGraph()

    #     browser = WebResource.WEB_BROWSER_HEADLESS
    #     browser.get(url)
    #     # self.html_source = browser.page_source
    #     # browser.quit()
    #     logging.debug(type(browser.page_source))
    #     print(browser.page_source)
    #     logging.info(f"Size of the parsed web page: {len(browser.page_source)}")



    #     try:
    #         element = browser.find_element_by_xpath(
    #             "//script[@type='application/ld+json']"
    #         )
    #         element = element.get_attribute("outerHTML")
    #         # browser.quit()

    #         tree = html.fromstring(element)
    #         jsonld_string = tree.xpath('//script[@type="application/ld+json"]//text()')
    #         print(jsonld_string)
    #         data = extruct.extract(
    #             browser.page_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
    #         )
    #         print(data)
    #         for json_ld_annots in jsonld_string:
    #             jsonld = json.loads(json_ld_annots)
    #             if type(jsonld) == list:
    #                 jsonld = jsonld[0]
    #             if "@context" in jsonld.keys():
    #                 if "//schema.org" in jsonld["@context"]:
    #                     jsonld["@context"] = WebResource.static_file_path
    #             kg.parse(
    #                 data=json.dumps(jsonld, ensure_ascii=False),
    #                 format="json-ld",
    #                 publicID=url,
    #             )
    #             logging.debug(f"{len(kg)} retrieved triples in KG")
    #             # logging.debug(kg.serialize(format="turtle"))

    #     except NoSuchElementException:
    #         logging.warning('Can\'t find "application/ld+json" content')
    #         pass

    #     kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
    #     kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
    #     kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

    #     return kg

    def __str__(self) -> str:
        out = """Web resource under FAIR assesment:\n\t"""
        out += self.url + "\n\t"
        out += str(len(self.rdf)) + " embedded RDF triples"
        return out
