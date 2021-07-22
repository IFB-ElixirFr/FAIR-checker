import unittest
from rdflib import Graph, ConjunctiveGraph, Namespace
import metrics.util as util


class GenSHACLTestCase(unittest.TestCase):
    def test_validate_shape_tool(self):
        turtle_edam = """
            @prefix biotools: <https://bio.tools/ontology/> .
            @prefix bsc: <http://bioschemas.org/> .
            @prefix edam: <http://edamontology.org/> .
            @prefix ns1: <http://www.w3.org/1999/xhtml/vocab#> .
            @prefix ns2: <http://ogp.me/ns#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix sc: <http://schema.org/> .
            @prefix xml: <http://www.w3.org/XML/1998/namespace> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            <file:///home/thomas/fair-checker/> ns2:description "Fast, accurate, memory-efficient aligner for short and long sequencing reads" ;
                ns2:image "" ;
                ns2:title "BWA" .

            <https://bio.tools/bwa> a sc:SoftwareApplication ;
                edam:has_input edam:data_2044,
                    edam:data_3210 ;
                edam:has_output edam:data_0863,
                    edam:data_1916,
                    edam:data_2012,
                    edam:data_3210 ;
                sc:additionalType "Command-line tool",
                    "Workbench" ;
                sc:applicationSubCategory edam:topic_0102 ;
                sc:citation <https://doi.org/10.1016/j.ygeno.2017.03.001>,
                    <https://doi.org/10.1093/bioinformatics/btp324>,
                    <https://doi.org/10.1093/bioinformatics/btp698>,
                    <https://doi.org/10.1093/bioinformatics/btu146>,
                    <https://doi.org/10.1186/1471-2105-14-184>,
                    <https://doi.org/10.1186/1471-2164-15-264>,
                    "pmcid:PMC2705234",
                    "pmcid:PMC3694458",
                    "pmcid:PMC4051166",
                    "pubmed:19451168",
                    "pubmed:20080505",
                    "pubmed:23758764",
                    "pubmed:24626854",
                    "pubmed:24708189",
                    "pubmed:28286147" ;
                sc:contributor <http://orcid.org/0000-0003-4874-2874> ;
                sc:description "Fast, accurate, memory-efficient aligner for short and long sequencing reads" ;
                sc:featureList edam:operation_0292,
                    edam:operation_3198,
                    edam:operation_3211,
                    edam:operation_3429 ;
                sc:license "MIT" ;
                sc:name "BWA" ;
                sc:operatingSystem "Linux",
                    "Mac" ;
                sc:softwareHelp <http://bio-bwa.sourceforge.net/bwa.shtml> ;
                sc:url "http://bio-bwa.sourceforge.net" ;
                biotools:primaryContact "bwa team" .

            <http://orcid.org/0000-0003-4874-2874> a <schema:Person> .

            <https://doi.org/10.1016/j.ygeno.2017.03.001> a sc:CreativeWork .

            <https://doi.org/10.1093/bioinformatics/btp324> a sc:CreativeWork .

            <https://doi.org/10.1093/bioinformatics/btp698> a sc:CreativeWork .

            <https://doi.org/10.1093/bioinformatics/btu146> a sc:CreativeWork .

            <https://doi.org/10.1186/1471-2105-14-184> a sc:CreativeWork .

            <https://doi.org/10.1186/1471-2164-15-264> a sc:CreativeWork .

            [] ns1:role ns1:alert .

            [] ns1:role ns1:navigation .
        """
        kg = ConjunctiveGraph()
        kg.parse(data=turtle_edam, format="turtle")

        query_classes = """
            SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
        """
        query_properties = """
            SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
        """

        table_content = {"classes": [], "properties": []}
        qres = kg.query(query_classes)
        print("Class")
        for row in qres:
            table_content["classes"].append({"name": row["class"], "tag": []})
            print(f'{row["class"]}')

        qres = kg.query(query_properties)
        print("Prop")
        for row in qres:
            table_content["properties"].append({"name": row["prop"], "tag": []})
            print(f'{row["prop"]}')

        for c in table_content['classes']:
            print(util.ask_BioPortal(c['name'], "class"))
            if util.ask_OLS(c['name']):
                c['tag'].append('OLS')
            if util.ask_LOV(c['name']):
                c['tag'].append('LOV')

        for p in table_content['properties']:
            print(util.ask_BioPortal(p['name'], "property"))
            # print(util.ask_OLS(p['name']))
            if util.ask_OLS(p['name']):
                p['tag'].append('OLS')
            if util.ask_LOV(p['name']):
                p['tag'].append('LOV')


if __name__ == "__main__":
    unittest.main()
