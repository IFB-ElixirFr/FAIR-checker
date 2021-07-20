from datetime import time
from ssl import SSLError

from metrics.test_metric import getMetrics, testMetric, requestResultSparql
from metrics.Evaluation import Evaluation

from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import extruct
from pathlib import Path

import rdflib
from rdflib import ConjunctiveGraph

import json

#########################
class AbstractFAIRMetrics(ABC):
    def __init__(self):
        self.name = "My name"
        self.id = "My id"
        self.desc = "My desc"
        self.principle = "My principle"
        self.creator = "My creeator name"
        self.created_at = "My creation date"
        self.updated_at = "My update date"
        self.html_source = "Page content"
        self.rdf_jsonld = "Graph RDF"
        self.requests_status_code = "Status code for requests"
        self.url = "URL here"


    #common functionality
    def common(self):
        print('In common method of Parent')

    # name
    def get_name(self):
        return self.name

    # desc
    def get_desc(self):
        return self.desc
        # print(f'Description: {self.desc}')

    def get_id(self):
        return self.id

    def get_principle(self):
        return self.principle

    def get_creator(self):
        return self.creator

    def get_creation_date(self):
        return self.created_at

    def get_update_date(self):
        return self.updated_at

    def get_requests_status_code(self):
        return self.requests_status_code

    def set_url(self, url):
        self.url = url

    def extract_html_requests(self):
        while (True):
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

        self.requests_status_code = response.status_code
        self.html_source = response.content



    def extract_html_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        browser = webdriver.Chrome(options=chrome_options)
        browser.get(self.url)

        self.html_source = browser.page_source

        browser.quit()

    def extract_rdf(self):
        html_source = self.html_source
        data = extruct.extract(html_source, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')
        kg = ConjunctiveGraph()

        base_path = Path(__file__).parent.parent  ## current directory
        static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())

        # kg = util.get_rdf_selenium(uri, kg)

        for md in data['json-ld']:
            if '@context' in md.keys():
                print(md['@context'])
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data['rdfa']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
        for md in data['microdata']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                    md['@context'] = static_file_path
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

        self.rdf_jsonld = kg

    # not all metrics can have an api
    @abstractmethod
    def get_api(self):
        pass

    # evaluations are not done the same way
    @abstractmethod
    def evaluate(self):
        pass

    def __str__(self):
        return f"FAIR metrics {self.id} : " \
               f"\n\t {self.principle} " \
               f"\n\t {self.name} " \
               f"\n\t {self.desc} " \
               f"\n\t {self.creator} " \
               f"\n\t {self.created_at} " \
               f"\n\t {self.updated_at} "
