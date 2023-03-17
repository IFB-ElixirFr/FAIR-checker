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
from rdflib.namespace import NamespaceManager
import requests
import time

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
import json
import os
import re

from json.decoder import JSONDecodeError

from metrics.util import clean_kg_excluding_ns_prefix

logger = logging.getLogger("DEV")


class WebResource:
    """
    Class that handle all operations related to a web resource based on its URL/URI, mainly retrieve all the RDF metadata from it, using HTML parsin as well as content-negociation

    """

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

    SERVER_TIMEOUT = 30

    status_code = None
    content_type = None
    mimetype = None
    browser_selenium = None
    html_content = None
    # html_selenium = None
    html_requests = None
    headers = None
    links_headers = None

    kg_var_strings = [
        "kg_links_header",
        "kg_mimetypes_match",
        "kg_rdfformats_match",
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
        """
        WebResource constructor, retrieve RDF metadata from the URL of the resource

        Args:
            url (str): The URL of the resource to retrieve RDF metadata from.
            rdf_graph (ConjuctiveGraph, optional): Allow to directly give a RDF Graph to instenciate the class. Defaults to None.
        """
        self.id = "WebResource Unique ID for cache"
        self.url = url

        # TODO rename variable
        self.kg_named_all = ConjunctiveGraph()

        # add the namespaces to the main RDF named graph
        self.kg_named_all.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.kg_named_all.namespace_manager.bind("scs", URIRef("https://schema.org/"))
        self.kg_named_all.namespace_manager.bind(
            "bsc", URIRef("https://bioschemas.org/")
        )
        self.kg_named_all.namespace_manager.bind(
            "dct", URIRef("http://purl.org/dc/terms/")
        )

        # Instanciate all sub_kg, one for each method of retrieving RDF metadata
        self.init_kgs()

        # If no RDF graph given
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

            cite_as, described_by, items = self.retrieve_links_from_headers()

            # get RDF from HTTP headers
            self.get_kg_from_header(described_by)

            # if not html, try to retrieve rdf from possible rdf format
            if mimetype != "text/html":
                # don't need to use selenium on non HTML content
                response = self.request_from_url(self.url)

                # generate rdf graph from mapped mimetypes
                for rdf_format in rdf_formats:
                    print(rdf_format)
                    self.kg_mimetypes_match = self.get_rdf_from_mimetype_match(
                        self.url, rdf_format, self.kg_mimetypes_match
                    )

                # if no rdf found: brutforce testing each RDF formats regardless of mimetypes
                if len(self.kg_mimetypes_match) == 0:
                    rdf_str = response.text
                    for rdf_format in self.RDF_MEDIA_TYPES_MAPPING.keys():
                        self.kg_rdfformats_match = self.get_rdf_from_mimetype_match(
                            url, rdf_format, self.kg_rdfformats_match
                        )

                logging.info(
                    "Resource content_type is: " + self.headers["Content-Type"]
                )

            # If the page is HTML
            elif mimetype == "text/html":
                # get all HTML with Selenium
                self.html_content = self.get_html_selenium(url)

                # if no links in headers try to get links from html
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
            else:
                # try get static RDF metadata (already available in html sources)
                self.html_content = self.request_from_url(self.url)
                self.html_to_rdf_extruct(self.html_content)

            # Add all 5 KG to a single named graph

            for s, p, o in self.kg_mimetypes_match:
                self.kg_named_all.add((s, p, o, URIRef(self.url + "#mimetypes_match")))

            for s, p, o in self.kg_rdfformats_match:
                self.kg_named_all.add((s, p, o, URIRef(self.url + "#rdfformats_match")))

            for s, p, o in self.kg_links_header:
                self.kg_named_all.add((s, p, o, URIRef(self.url + "#links_header")))

            for s, p, o in self.kg_links_html:
                self.kg_named_all.add((s, p, o, URIRef(self.url + "#links_html")))

            for s, p, o in self.kg_html:
                self.kg_named_all.add((s, p, o, URIRef(self.url + "#html")))

            # clean name graph from a specific prefix
            self.kg_named_all = clean_kg_excluding_ns_prefix(
                self.kg_named_all, "http://www.w3.org/1999/xhtml/vocab#"
            )

            # Logging not working need to be replace by dev_logger
            logging.info("HTML: " + str(len(self.kg_html)))
            logging.info("LINKS HEADERS: " + str(len(self.kg_links_header)))
            logging.info("MIMETYPES: " + str(len(self.kg_mimetypes_match)))
            logging.info("RDF FORMATS: " + str(len(self.kg_rdfformats_match)))
            logging.info("LINKS HTML: " + str(len(self.kg_links_html)))

        else:
            self.rdf = rdf_graph

        self.rdf.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.rdf.namespace_manager.bind("scs", URIRef("https://schema.org/"))
        self.rdf.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        self.rdf.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
        self.rdf = clean_kg_excluding_ns_prefix(
            self.rdf, "http://www.w3.org/1999/xhtml/vocab#"
        )

    def init_kgs(self):
        """
        Create variables which are rdflib RDF graphs, using a string list as there names, and set namespaces for each graph.
        """

        for var_str in self.kg_var_strings:

            setattr(
                WebResource,
                var_str,
                ConjunctiveGraph(),
            )

            getattr(WebResource, var_str).namespace_manager.bind(
                "sc", URIRef("http://schema.org/")
            )
            getattr(WebResource, var_str).namespace_manager.bind(
                "scs", URIRef("https://schema.org/")
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
        """
        Get the RDF parsing the HTTP headers

        Args:
            described_by (str): The described_by attribute content in HTTP headers
        """

        for link in described_by:

            reg_string = '<(.*?)>*;*rel="(.*?)"*;*type="(.*?)"'
            p = re.compile(reg_string)
            match = re.search(reg_string, link)
            url = match.group(1)
            rel = match.group(2)
            link_mimetype = match.group(3)

            # Use headers link mimetype to get corresponding rdf_formats
            rdf_formats = self.get_rdf_format_from_contenttype(link_mimetype)

            # For each RDF format, try to parse the RDF using these formats
            for rdf_format in rdf_formats:
                self.get_rdf_from_mimetype_match(url, rdf_format, self.kg_links_header)

    def get_url(self):
        """
        Get the URL used to instantiate the WebResource

        Returns:
            str: The URL of the WebResource
        """
        return self.url

    def get_rdf(self):
        """
        Get the RDF graph metadata of the WebResource

        Returns:
            ConjunctiveGraph: The named graph instance with all RDF metadata found
        """
        return self.kg_named_all

    def get_kg_mimetypes_match(self):
        """
        Get the RDF sub graph metadata aggregate that used the mimetype to determine the RDF format

        Returns:
            ConjunctiveGraph: The RDF graph that contains the metadata using this method
        """
        return self.kg_mimetypes_match

    def get_kg_html(self):
        """
        Get the RDF sub graph metadata aggregate that used the HTML parsing

        Returns:
            ConjunctiveGraph: The RDF graph that contains the metadata using this method
        """
        return self.kg_html

    def get_kg_rdfformats_match(self):
        """
        Get the RDF sub graph metadata aggregate that used the method of trying every RDF format to find one working (brutforce method)

        Returns:
            ConjunctiveGraph: The RDF graph that contains the metadata using this method
        """
        return self.kg_rdfformats_match

    def get_kg_links_header(self):
        """
        Get the RDF sub graph metadata aggregate that used links found in headers

        Returns:
            ConjunctiveGraph: The RDF graph that contains the metadata using this method
        """
        return self.kg_links_header

    def get_kg_links_html(self):
        """
        Get the RDF sub graph metadata aggregate that used the links found in HTML

        Returns:
            ConjunctiveGraph: The RDF graph that contains the metadata using this method
        """
        return self.kg_links_html

    def get_status_code(self):
        """
        Get the status code of the URL used to instantiate the WebResource

        Returns:
            int: The status_code of the resource
        """
        return self.status_code

    def get_html_content(self):
        """
        Get the HTML content of the web resource

        Returns:
            str: HTML content of the given URL
        """
        return self.html_content

    def get_http_header(self):
        """
        Get the headers corresponding to the URL used to instantiate the WebResource

        Returns:
            list: Headers of the web resource given by requests.head()
        """
        return self.headers

    @staticmethod
    def is_schema_http(kg):
        """
        Check if the RDF graph used http or https for the schema.org namespace

        Args:
            kg (ConjunctiveGraph): The graph to check HTTP(S) for

        Returns:
            bool: True if the schema.org used is HTTP, False if HTTPS
        """
        for s, p, o, g in kg.quads(None):
            if str(s).startswith("http://schema.org"):
                return True
            if str(p).startswith("http://schema.org"):
                return True
            if isinstance(o, rdflib.URIRef):
                if str(o).startswith("http://schema.org"):
                    return True
        return False

    # Could be a static method
    def schema_https_convert(self, kg):
        """
        Method to convert all http://schema.org URIRef to https

        Args:
            kg (ConjunctiveGraph): The graph to check HTTP(S) for

        Returns:
            ConjunctiveGraph: The updated KG with https://schema.org URIRef instead of http
        """
        for s, p, o, g in kg.quads(None):
            changed = False
            new_s = s
            if str(s).startswith("http://schema.org"):
                new_s = rdflib.URIRef(str(s).replace("http", "https", 1))
                changed = True
            new_p = p
            if str(p).startswith("http://schema.org"):
                new_p = rdflib.URIRef(str(p).replace("http", "https", 1))
                changed = True
            new_o = o
            if isinstance(o, rdflib.URIRef):
                if str(o).startswith("http://schema.org"):
                    new_o = rdflib.URIRef(str(o).replace("http", "https", 1))
                    changed = True
            if changed:
                kg.remove((s, p, o, g))
                kg.add((new_s, new_p, new_o, g))
        return kg

    # Might change the name bcause it is not a "getter"
    def get_rdf_from_mimetype_match(self, url, rdf_format, kg):
        """
        Retrieve RDF metadata using RDF format found from mimetype mapping

        Args:
            url (str): URL of the WebResource
            rdf_format (str): RDF format to be used for the rdflib parse method
            kg (ConjunctiveGraph): The graph to add found RDF metadata

        Returns:
            ConjunctiveGraph: The graph containing the RDF metadata using the mimetype to rdf format mapping
        """
        logging.debug("Getting RDF from: " + rdf_format)

        # Create a temp graph because parsing directly in the main graph seems to override some of the previous content
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

            except Exception as err:
                # if error UnicodeDecodeError execute following code, otherwise continue to next format
                # Should not happen anymore with the latest rdflib version
                if type(err).__name__ == "UnicodeDecodeError":
                    kg = self.handle_unicodedecodeerror(url, kg, response)

        return kg

    def get_rdf_format_from_contenttype(self, mimetype):
        """
        List all RDF format for rdflib that are mapping to the mimetype found in headers

        Args:
            mimetype (str): The mimetype found in headers

        Returns:
            list: A list of possible RDF format to use for parsing
        """

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
        """
        WARNING: Used previously to fix a bug which should not be present anymore in latest version of RDFlib used
        Should consider to deprecate this method

        Args:
            url (str): URL of the web resource
            kg (ConjunctiveGraph): KG to store RDF metadata
            response (_type_): Response of web page requests giving this error while rdflib parsing after extruct

        Returns:
            ConjunctiveGraph: Updated KG with fixed namespace
        """

        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())
        json_response = response.json()

        if "@context" in json_response.keys():
            if ("https://schema.org" in json_response["@context"]) or (
                "http://schema.org" in json_response["@context"]
            ):
                json_response["@context"] = self.static_file_path

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
        """
        Retrieve links attributes from headers parsing.

        Returns:
            tuple: Tuple containing cite_as, discribed_by and item links headers
        """
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
                    links_col.append(link)
                    tokens = link.split(";")
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
        """
        Retrieve links attributes from HTML parsing.

        Returns:
            list: List containing links attributes: describedby, cite-as, item
        """
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
        """
        Get the content of the web page using URL given to instantiate the WebResource, handles timeout et some errors and retry a maximum number of times

        Args:
            url (str): The URL given to instantiate the WebResource

        Returns:
            requests.response: The response object of the requests
        """
        nb_retry = 0
        while nb_retry < 3:
            try:
                nb_retry += 1
                response = requests.get(url=url, timeout=30, verify=False)
                break
            except SSLError:
                time.sleep(5)
            except requests.exceptions.Timeout:
                logging.warning("Timeout, retrying")
                time.sleep(5)
            except requests.exceptions.ConnectionError as e:
                logging.warning(e)
                logging.warning("ConnectionError, retrying...")
                time.sleep(10)

        return response

    # Might change the name bcause it is not a "getter"
    def get_html_selenium(self, url):
        """
        Retrieve all the HTML content using Selenium

        Args:
            url (str): The URL used to instantiate the WebResource

        Returns:
            str: The HTML content of the web page
        """
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.get(url)
        # Used to let time to javascript to be executed (e.g. Selenium don't load consistantly, can't consistantly find RDF without it)
        # Can be improved with other mean of dynamically waiting for loading to finish
        time.sleep(2)

        browser.set_page_load_timeout(30)
        browser.implicitly_wait(30)

        # Seems to not be actually working as intended (Dynamic page load wait to let all javascript executing)
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
        """
        Create an RDF graph using metadata found in the HTML of the web page

        Args:
            html_source (str): The HTML content of the web page

        Returns:
            ConjunctiveGraph: The RDF sub graph containing RDF obtained from HTML parsing (RDFa, microdata, JSON-LD)
        """
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

        kg_microdata = ConjunctiveGraph()

        if "microdata" in data.keys():
            for md in data["microdata"]:
                kg_microdata.parse(
                    data=json.dumps(md, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )

        kg_extruct = kg_jsonld + kg_rdfa + kg_microdata

        for s, p, o in kg_extruct:
            self.kg_html.add((s, p, o))

        return self.kg_html

    def __str__(self) -> str:
        """
        The __str__ method

        Returns:
            str: The string returned
        """

        out = """Web resource under FAIR assesment:\n\t"""
        out += self.url + "\n\t"
        out += str(len(self.rdf)) + " embedded RDF triples"
        return out
