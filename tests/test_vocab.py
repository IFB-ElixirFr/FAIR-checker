import unittest
from rdflib import BNode, ConjunctiveGraph, URIRef
import metrics.util as util
from metrics.WebResource import WebResource


class CommunityVocabTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

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
    query_classes = """
        SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
    """
    query_properties = """
        SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
    """

    def test_OLS(self):
        turtle_edam = self.turtle_edam
        kg = ConjunctiveGraph()
        kg.parse(data=turtle_edam, format="turtle")

        query_classes = self.query_classes
        query_properties = self.query_properties

        table_content = {"classes": [], "properties": []}
        qres = kg.query(query_classes)

        for row in qres:
            table_content["classes"].append({"name": row["class"], "tag": []})

        qres = kg.query(query_properties)
        for row in qres:
            table_content["properties"].append({"name": row["prop"], "tag": []})

        class_or_property_found = False
        for c in table_content["classes"]:
            if util.ask_OLS(c["name"]):
                c["tag"].append("OLS")
                class_or_property_found = True
        for p in table_content["properties"]:
            if util.ask_OLS(p["name"]):
                p["tag"].append("OLS")
                class_or_property_found = True

        self.assertTrue(class_or_property_found, True)

    def test_LOV(self):
        turtle_edam = self.turtle_edam
        kg = ConjunctiveGraph()
        kg.parse(data=turtle_edam, format="turtle")

        query_classes = self.query_classes
        query_properties = self.query_properties

        table_content = {"classes": [], "properties": []}
        qres = kg.query(query_classes)

        for row in qres:
            table_content["classes"].append({"name": row["class"], "tag": []})
            print(f'{row["class"]}')

        qres = kg.query(query_properties)
        print("Prop")
        for row in qres:
            table_content["properties"].append({"name": row["prop"], "tag": []})
            print(f'{row["prop"]}')

        class_or_property_found = False
        for c in table_content["classes"]:
            if util.ask_LOV(c["name"]):
                c["tag"].append("LOV")
                class_or_property_found = True
        for p in table_content["properties"]:
            if util.ask_LOV(p["name"]):
                p["tag"].append("LOV")
                class_or_property_found = True

        self.assertTrue(class_or_property_found, True)

    # TODO find a solution
    @unittest.skip("Need API key to work")
    def test_BioPortal(self):
        turtle_edam = self.turtle_edam
        kg = ConjunctiveGraph()
        kg.parse(data=turtle_edam, format="turtle")

        query_classes = self.query_classes
        query_properties = self.query_properties

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

        for c in table_content["classes"]:
            if util.ask_BioPortal(c["name"], "class"):
                c["tag"].append("BioPortal")

        for p in table_content["properties"]:
            if util.ask_BioPortal(c["name"], "property"):
                c["tag"].append("BioPortal")

    def test_exclude_ns_prefix(self):
        turtle_edam = self.turtle_edam
        kg = ConjunctiveGraph()
        kg.parse(data=turtle_edam, format="turtle")
        # KG contains 2 xhtml triples

        ns = "http://www.w3.org/1999/xhtml/vocab#"
        cleaned_kg = util.clean_kg_excluding_ns_prefix(kg, ns)
        # cleaned KG should contain 0 xhtml triples

        self.assertEquals(len(kg) - 2, len(cleaned_kg))

    def test_exclude_xhtml(self):
        ns = "http://www.w3.org/1999/xhtml/vocab#"
        kg = ConjunctiveGraph()
        kg.add(
            (
                BNode(),
                URIRef("http://www.w3.org/1999/xhtml/vocab#role"),
                URIRef("http://www.w3.org/1999/xhtml/vocab#button"),
            )
        )
        print(kg.serialize(format="turtle"))

        q_xhtml = (
            'SELECT * WHERE { ?s ?p ?o . FILTER (strstarts(str(?p), "' + ns + '"))}'
        )
        print(q_xhtml)

        res = kg.query(q_xhtml)
        self.assertEquals(len(res), 1)

        q_del = (
            'DELETE {?s ?p ?o} WHERE { ?s ?p ?o . FILTER (strstarts(str(?p), "'
            + ns
            + '"))}'
        )
        kg.update(q_del)
        print(kg.serialize(format="turtle"))

        res = kg.query(q_xhtml)
        self.assertEquals(len(res), 0)


if __name__ == "__main__":
    unittest.main()
