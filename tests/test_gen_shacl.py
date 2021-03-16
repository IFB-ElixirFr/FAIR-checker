import unittest
from rdflib import ConjunctiveGraph
from jinja2 import Template
from pyshacl import validate

from metrics.R2Impl import R2Impl

class GenSHACLTestCase(unittest.TestCase):

    """to match an RDF resource, use sh:targetClass or sh:targetSubjectOf"""

    accessibility_properties = ['schema:licenses']

    shape_template = """
        @prefix dash: <http://datashapes.org/dash#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix schema: <http://schema.org/> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix edam: <http://edamontology.org/> .
        @prefix biotools: <https://bio.tools/ontology/> .

        schema:AccessibilityShape
            a sh:NodeShape ;
            #sh:targetSubjectsOf schema:name ;
            sh:targetClass schema:ComputationalWorkflow, schema:SoftwareApplication ;

            {% for prop_name in data['properties'] %}
            sh:property [
                sh:path {{prop_name}} ;
                sh:minCount 1 ;
                sh:severity sh:Violation
            ] ;
            {% endfor %}
        .
    """

    def gen_SHACL_from_prop(self, property_list=None):
        r2_1 = R2Impl()
        r2_1.set_url("https://workflowhub.eu/workflows/45")
        r2_1.extract_html_requests()
        r2_1.extract_rdf()
        kg1 = r2_1.get_jsonld()

        #r2_2 = R2Impl()
        #r2_2.set_url("https://bio.tools/jaspar")
        #r2_2.extract_html_requests()
        #r2_2.extract_html_selenium()
        #r2_2.extract_rdf()
        #kg2 = r2_2.get_jsonld()

        kg2 = ConjunctiveGraph()
        kg2.parse(location='https://bio.tools/api/jaspar?format=jsonld',format='json-ld')

        kg = kg1 + kg2

        print(kg.serialize(format="turtle").decode())
        # print(len(kg1))
        #print(len(kg2))
        #print(kg2.serialize(format="turtle").decode())
        #print(len(kg))

        data = {
            'properties': self.accessibility_properties,
        }

        template = Template(self.shape_template)
        shape = template.render(data=data)
        print(shape)
        g = ConjunctiveGraph()
        g.parse(data=shape, format='turtle')
        print(len(g))

        r = validate(data_graph=kg,
                     data_graph_format='turtle',
                     shacl_graph=shape,
                     # shacl_graph = my_shacl_constraint,
                     shacl_graph_format='turtle',
                     ont_graph=None,
                     inference='rdfs',
                     abort_on_error=False,
                     meta_shacl=False,
                     debug=True)

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
        #print('VALIDATION RESULTS')
        #print(results_text)
        #print(conforms)
        #print(results_graph.serialize(format="turtle").decode())
        warnings = []
        errors = []
        for r in results:
            if "#Warning" in r['severity']:
                print(f'WARNING = Property {r["path"]} should be provided for {r["node"]}')
            if "#Violation" in r['severity']:
                print(f'ERROR = Property {r["path"]} must be provided for {r["node"]}')


    def test_something(self):
        self.gen_SHACL_from_prop(self)



if __name__ == '__main__':
    unittest.main()
