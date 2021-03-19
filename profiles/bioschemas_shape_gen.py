import time
from ssl import SSLError

import extruct
import json
from rdflib import ConjunctiveGraph
from jinja2 import Template
from pyshacl import validate
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics


def get_html_from_requests(url):
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

    return response.content, response.status_code


def get_html_from_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    try:
        browser.get(url)
        return browser.page_source

    finally:
        browser.quit()


def get_rdf(html_source):
    # data = extruct.extract(html_source, syntaxes=['microdata', 'rdfa', 'json-ld'], )
    data = extruct.extract(str(html_source), syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')
    kg = ConjunctiveGraph()

    # kg = util.get_rdf_selenium(uri, kg)
    #print(html_source)
    #print(data.keys())

    if 'json-ld' in data.keys():
        for md in data['json-ld']:
            if '@context' in md.keys():
                print(md['@context'])
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    if 'rdfa' in data.keys():
        for md in data['rdfa']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    if 'microdata' in data.keys():
        for md in data['microdata']:
            if '@context' in md.keys():
                if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']):
                    md['@context'] = '../static/data/jsonldcontext.json'
            kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    return kg

def checktype(obj):
    # This if statement makes sure input is a list that is not empty
    if obj and isinstance(obj, list):
        return all(isinstance(s, str) for s in obj)
    else:
        return False

def gen_SHACL_from_profile(shape_name, target_classes, min_props, rec_props):

    #TODO type checking for parameters
    #print(shape_name)
    #print(target_classes)
    #print(min_props)
    #print(rec_props)

    shape_template = """
        @prefix dash: <http://datashapes.org/dash#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix schema: <http://schema.org/> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix edam: <http://edamontology.org/> .
        @prefix biotools: <https://bio.tools/ontology/> .

        schema:{{shape_name}}
            a sh:NodeShape ;
            #sh:targetSubjectsOf schema:name ;
            {% for c in target_classes %}
            sh:targetClass  {{c}} ;
            {% endfor %}

            {% for min_prop in min_props %}
            sh:property [
                sh:path {{min_prop}} ;
                sh:minCount 1 ;
                sh:severity sh:Violation
            ] ;
            {% endfor %}
            
            {% for rec_prop in rec_props %}
            sh:property [
                sh:path {{rec_prop}} ;
                sh:minCount 1 ;
                sh:severity sh:Violation
            ] ;
            {% endfor %}
        .
    """

    template = Template(shape_template)
    shape = template.render(shape_name=shape_name, target_classes=target_classes, min_props=min_props, rec_props=rec_props)
    #print(shape)

    #todo try catch to validate the generated shape
    g = ConjunctiveGraph()
    g.parse(data=shape, format='turtle')

    return shape

def validate_shape_from_RDF(input_uri, rdf_syntax, shacl_shape):
    kg = ConjunctiveGraph()
    kg.parse(location=input_uri, format=rdf_syntax)
    validate_shape(knowledge_graph=kg, shacl_shape=shacl_shape)

def validate_shape_from_microdata(input_uri, shacl_shape):
    #html = get_html_from_requests(input_uri)
    html = get_html_from_selenium(input_uri)
    kg = get_rdf(html)
    #print(kg.serialize(format='turtle').decode())
    validate_shape(knowledge_graph=kg, shacl_shape=shacl_shape)

def validate_shape(knowledge_graph, shacl_shape):

    r = validate(data_graph=knowledge_graph,
                 data_graph_format='turtle',
                 shacl_graph=shacl_shape,
                 # shacl_graph = my_shacl_constraint,
                 shacl_graph_format='turtle',
                 ont_graph=None,
                 inference='rdfs',
                 abort_on_error=False,
                 meta_shacl=False,
                 debug=False)

    conforms, results_graph, results_text = r

    report_query = """
            SELECT ?node ?path ?severity WHERE {
                ?v rdf:type sh:ValidationReport ;
                   sh:result ?r .
                ?r sh:focusNode ?node ;
                   sh:sourceShape ?s .
                ?s sh:path ?path ;
                   sh:severity ?severity .
            }
        """

    results = results_graph.query(report_query)
    # print('VALIDATION RESULTS')
    # print(results_text)
    # print(conforms)
    # print(results_graph.serialize(format="turtle").decode())
    warnings = []
    errors = []
    for r in results:
        if "#Warning" in r['severity']:
            print(f'WARNING = Property {r["path"]} should be provided for {r["node"]}')
        if "#Violation" in r['severity']:
            print(f'ERROR = Property {r["path"]} must be provided for {r["node"]}')