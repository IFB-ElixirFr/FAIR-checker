import unittest

from rdflib import ConjunctiveGraph, URIRef
from jinja2 import Template
from pyshacl import validate
import json

from profiles.bioschemas_shape_gen import gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import gen_SHACL_from_target_class
from profiles.bioschemas_shape_gen import validate_shape
from profiles.bioschemas_shape_gen import validate_shape_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_KG
from profiles.bioschemas_shape_gen import validate_any_from_microdata
from profiles.bioschemas_shape_gen import validate_shape_from_microdata

from metrics.WebResource import WebResource


class GenSHACLTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_validate_rocrate(self):

        test_graph = { "@context": "https://w3id.org/ro/crate/1.1/context", 
            "@graph": [
                {
                "@type": "CreativeWork",
                "@id": "ro-crate-metadata.json",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
                "about": {"@id": "./"}
                },
                {
                "@id": "./",
                "@type": "Dataset",
                "hasPart": [
                    { "@id": "workflow/alignment.knime" }
                ]
                },
                {
                "@id": "workflow/alignment.knime",  
                "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"],
                "conformsTo": 
                    {"@id": "https://bioschemas.org/profiles/ComputationalWorkflow/0.5-DRAFT-2020_07_21/"},
                "name": "Sequence alignment workflow",
                "programmingLanguage": {"@id": "#knime"},
                "creator": {"@id": "#alice"},
                "dateCreated": "2020-05-23",
                "license": { "@id": "https://spdx.org/licenses/CC-BY-NC-SA-4.0"},
                "input": [
                    { "@id": "#36aadbd4-4a2d-4e33-83b4-0cbf6a6a8c5b"}
                ],
                "output": [
                    { "@id": "#6c703fee-6af7-4fdb-a57d-9e8bc4486044"},
                    { "@id": "#2f32b861-e43c-401f-8c42-04fd84273bdf"}
                ],
                "sdPublisher": {"@id": "#workflow-hub"},
                "url": "http://example.com/workflows/alignment",
                "version": "0.5.0"
                },
                {
                "@id": "#36aadbd4-4a2d-4e33-83b4-0cbf6a6a8c5b",
                "@type": "FormalParameter",
                "conformsTo": {"@id": "https://bioschemas.org/profiles/FormalParameter/0.1-DRAFT-2020_07_21/"},
                "name": "genome_sequence",
                "valueRequired": "true",
                "additionalType": {"@id": "http://edamontology.org/data_2977"},
                "format": {"@id": "http://edamontology.org/format_1929"}
                },
                {
                "@id": "#6c703fee-6af7-4fdb-a57d-9e8bc4486044",
                "@type": "FormalParameter",
                "conformsTo": {"@id": "https://bioschemas.org/profiles/FormalParameter/0.1-DRAFT-2020_07_21/"},
                "name": "cleaned_sequence",
                "additionalType": {"@id": "http://edamontology.org/data_2977"},
                "encodingFormat": {"@id": "http://edamontology.org/format_2572"}
                },
                {
                "@id": "#2f32b861-e43c-401f-8c42-04fd84273bdf",
                "@type": "FormalParameter",
                "conformsTo": {"@id": "https://bioschemas.org/profiles/FormalParameter/0.1-DRAFT-2020_07_21/"},
                "name": "sequence_alignment",
                "additionalType": {"@id": "http://edamontology.org/data_1383"},
                "encodingFormat": {"@id": "http://edamontology.org/format_1982"}
                },
                {
                "@id": "https://spdx.org/licenses/CC-BY-NC-SA-4.0",
                "@type": "CreativeWork",
                "name": "Creative Commons Attribution Non Commercial Share Alike 4.0 International",
                "alternateName": "CC-BY-NC-SA-4.0"
                },
                {
                "@id": "#knime",
                "@type": "ProgrammingLanguage",
                "name": "KNIME Analytics Platform",
                "alternateName": "KNIME",
                "url": "https://www.knime.com/whats-new-in-knime-41",
                "version": "4.1.3"
                },
                {
                "@id": "#alice",
                "@type": "Person",
                "name": "Alice Brown"
                },
                {
                "@id": "#workflow-hub",
                "@type": "Organization",
                "name": "Example Workflow Hub",
                "url":"http://example.com/workflows/"
                },
                {
                "@id": "http://edamontology.org/format_1929",
                "@type": "Thing",
                "name": "FASTA sequence format"
                },
                {
                "@id": "http://edamontology.org/format_1982",
                "@type": "Thing",
                "name": "ClustalW alignment format"
                },
                {
                "@id": "http://edamontology.org/format_2572",
                "@type": "Thing",
                "name": "BAM format"
                },
                {
                "@id": "http://edamontology.org/data_2977",
                "@type": "Thing",
                "name": "Nucleic acid sequence"
                },
                {
                "@id": "http://edamontology.org/data_1383",
                "@type": "Thing",
                "name": "Nucleic acid sequence alignment"
                }
            ]
            }


        g_test = ConjunctiveGraph()
        g_test.parse(data=json.dumps(test_graph), format="json-ld")

        shape_name = "ROCDatasetShape"
        target_classes = []

        # hasPart should be: File,SoftwareSourceCode,ComputationalWorkflow
        # mainEntity should be: File,SoftwareSourceCode,ComputationalWorkflow
        min_props = ["hasPart", "mainEntity"]
        rec_props = []


        # need to use sh:datatype in shape for hasPart and mainEntity
        shape_template = """
            @prefix ns: <https://fair-checker.france-bioinformatique.fr#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix sc: <http://schema.org/> .
            @prefix bsc: <https://bioschemas.org/> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            @prefix edam: <http://edamontology.org/> .
            @prefix biotools: <https://bio.tools/ontology/> .

            ns:{{shape_name}}
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
                    sh:severity sh:Warning
                ] ;
                {% endfor %}
            .
        """

        template = Template(shape_template)
        shape = template.render(
            shape_name=shape_name,
            target_classes=target_classes,
            min_props=min_props,
            rec_props=rec_props,
        )

        validate_shape(g_test, shape)

    def test_validate_shape_tool(self):
        classes = ["sc:SoftwareApplication"]
        minimal_software_properties = ["sc:name", "sc:description", "sc:url"]
        recommended_software_properties = [
            "sc:additionalType",
            "sc:applicationCategory",
            "sc:applicationSubCategory",
            "sc:author" "sc:license",
            "sc:citation",
            "sc:featureList",
            "sc:softwareVersion",
        ]

        shape = gen_SHACL_from_profile(
            "toolShape",
            target_classes=classes,
            min_props=minimal_software_properties,
            rec_props=recommended_software_properties,
        )

        self.assertTrue("sc:license" in shape)

        conforms, warnings, errors = validate_shape_from_RDF(
            input_uri="https://bio.tools/api/jaspar?format=jsonld",
            rdf_syntax="json-ld",
            shacl_shape=shape,
        )

        self.assertFalse(conforms)
        self.assertEqual(len(warnings), 4)
        self.assertEqual(len(errors), 3)

    def test_validate_shape_dataset(self):
        classes = ["sc:Dataset"]
        minimal_dataset_properties = [
            "sc:name",
            "sc:description",
            "sc:identifier",
            "sc:keywords",
            "sc:url",
        ]
        recommended_dataset_properties = ["sc:license", "sc:creator", "sc:citation"]

        shape = gen_SHACL_from_profile(
            "datasetShape",
            target_classes=classes,
            min_props=minimal_dataset_properties,
            rec_props=recommended_dataset_properties,
        )
        conforms, warnings, errors = validate_shape_from_microdata(
            input_uri="https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ",
            shacl_shape=shape,
        )

        if conforms:
            print("SHACL validation ok")
        else:
            print("Failed SHACL validation")

        self.assertTrue(conforms)

    def test_generate_right_shape(self):
        target_class = "sc:SoftwareApplication"
        shape, ref_profile = gen_SHACL_from_target_class(target_class=target_class)
        self.assertTrue("sh:path" in shape)

    def test_biotools_validation(self):
        res = validate_any_from_RDF(
            input_url="https://bio.tools/api/jaspar?format=jsonld", rdf_syntax="json-ld"
        )
        self.assertGreater(len(res), 0)
        self.assertEquals(len(res["https://bio.tools/jaspar"]["warnings"]), 5)
        self.assertEquals(len(res["https://bio.tools/jaspar"]["errors"]), 3)

    def test_pangaea_validation(self):
        res = validate_any_from_microdata(
            input_url="https://doi.pangaea.de/10.1594/PANGAEA.914331"
        )
        self.assertGreater(len(res[0]), 0)
        self.assertEquals(
            len(res[0]["https://doi.org/10.1594/PANGAEA.914331"]["errors"]), 0
        )

    def test_datacite_validation(self):
        res = validate_any_from_microdata(
            input_url="https://search.datacite.org/works/10.7892/boris.108387"
        )
        self.assertGreater(len(res[0]), 0)
        self.assertFalse(res[0]["https://doi.org/10.7892/boris.108387"]["conforms"])
        self.assertEquals(
            len(res[0]["https://doi.org/10.7892/boris.108387"]["errors"]), 2
        )
        self.assertEquals(
            len(res[0]["https://doi.org/10.7892/boris.108387"]["warnings"]), 11
        )

    def test_datacite_validation_kg(self):
        input_url = "https://search.datacite.org/works/10.7892/boris.108387"
        datacite_md = WebResource(input_url)
        kg = datacite_md.get_rdf()

        print(f"{len(kg)} loaded RDF triples")
        print(kg.serialize(format="turtle"))
        res = validate_any_from_KG(kg=kg)
        self.assertGreater(len(res), 0)
        self.assertFalse(res["https://doi.org/10.7892/boris.108387"]["conforms"])
        self.assertEquals(len(res["https://doi.org/10.7892/boris.108387"]["errors"]), 2)
        self.assertEquals(
            len(res["https://doi.org/10.7892/boris.108387"]["warnings"]), 11
        )

    def test_inrae_dataverse_validation(self):
        res = validate_any_from_microdata(
            input_url="https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ"
        )
        self.assertEqual(len(res[0]), 0)

    def test_workflow_validation(self):
        res = validate_any_from_microdata(
            input_url="https://workflowhub.eu/workflows/263"
        )
        self.assertEqual(
            len(res[0]["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 4
        )

    def test_base_prefix_rdf(self):
        rdf = """
        @prefix rdfs: <http://my/prefix/> .
        <test> rdfs:label "toto" .
        <#test> <http://schema.org/label> "toto" .
        """
        print()
        print()
        kg = ConjunctiveGraph()
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.parse(data=rdf, format="turtle")
        print(kg.serialize(format="turtle"))
        for s, p, o in kg:
            print(f"{s} {p} {o}")

        self.assertTrue("sc:" in kg.serialize(format="turtle"))
        self.assertTrue("file:///" in kg.serialize(format="turtle"))

        if "@base" not in kg.serialize(format="turtle"):
            new_rdf = "@base <http://fair-checker/> .\n" + rdf
            kg = ConjunctiveGraph()
            kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
            kg.parse(data=new_rdf, format="turtle")
            print(kg.serialize(format="turtle", base="http://fair-checker/"))

        self.assertTrue(
            "file:///" not in kg.serialize(format="turtle", base="http://fair-checker/")
        )


if __name__ == "__main__":
    unittest.main()
