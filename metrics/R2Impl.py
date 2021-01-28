from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import extruct

import rdflib
from rdflib import ConjunctiveGraph

import json

from metrics.util import ask_LOV

class R2Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    Check that how classes and properties are known in major standards, as reported in LOV :
       1. extract RDF annotations from web page
       2. list all used RDFS / OWL classes : ?class matching triple pattern ( ?x rdf:type ?class)
       3. list all used RDFS / OWL properties : ?p matching triple pattern ( ?s ?p ?o)
       4. for each, ask (efficiently) if it's known in LOV
    """


    def __init__(self):
        self.name = "R2"
        self.url = "URL here"
        self.html_source = "Page content"
        self.api = "api_url_for_R2"
        self.rdf_jsonld = "Graph RDF"

    def extract_html_requests(self, url):
        while (True):
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

        self.html_source = response.content

    def extract_html_selenium(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        browser = webdriver.Chrome(options=chrome_options)
        browser.get(url)

        self.html_source = browser.page_source

        browser.quit()



    def extract_rdf(self):
        html_source = self.html_source
        data = extruct.extract(html_source, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')
        kg = ConjunctiveGraph()

        # kg = util.get_rdf_selenium(uri, kg)

        for md in data['json-ld']:
            if '@context' in md.keys():
                print(md['@context'])
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data['rdfa']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data['microdata']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        self.rdf_jsonld = kg

    def get_classes(self):
        query_classes = """
            SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
        """

        return self.rdf_jsonld.query(query_classes)

    def get_properties(self):
        query_properties = """
            SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
        """

        return self.rdf_jsonld.query(query_properties)


    def get_api(self):
        return self.api

    def get_html_source(self):
        return self.html_source

    def get_jsonld(self):
        return self.rdf_jsonld

    def ask_LOV(self):
        # ask_LOV()
        return "Me too"

    def evaluate(self):
        print("Evaluating R2")
