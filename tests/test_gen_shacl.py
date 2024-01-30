import unittest

from rdflib import ConjunctiveGraph, URIRef

from profiles.bioschemas_shape_gen import gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import gen_SHACL_from_target_class
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

    def test_validate_shape_tool(self):
        classes = ["sc:SoftwareApplication"]
        minimal_software_properties = ["sc:citation"]
        recommended_software_properties = [
            "sc:applicationSubCategory",
            "sc:license",
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
        print(errors)
        print(warnings)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(len(errors), 0)

    @unittest.skip("Testing method no longer used")
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

    # @unittest.skip("Issue with parsing remote bio.tools jsonld")
    def test_biotools_validation(self):
        res = validate_any_from_RDF(
            input_url="https://bio.tools/api/jaspar?format=jsonld", rdf_syntax="json-ld"
        )
        self.assertGreater(len(res), 0)
        self.assertEqual(len(res["https://bio.tools/jaspar"]["warnings"]), 5)
        self.assertEqual(len(res["https://bio.tools/jaspar"]["errors"]), 3)

    @unittest.skip("Max retries exceeded with url: /10.1594/PANGAEA.914331")
    def test_pangaea_validation(self):
        res = validate_any_from_microdata(
            input_url="https://doi.pangaea.de/10.1594/PANGAEA.914331"
        )
        self.assertGreater(len(res[0]), 0)
        self.assertEqual(
            len(res[0]["https://doi.org/10.1594/PANGAEA.914331"]["errors"]), 0
        )

    def test_datacite_validation(self):
        res = validate_any_from_microdata(
            input_url="https://commons.datacite.org/doi.org/10.7892/boris.108387"
        )
        self.assertGreater(len(res[0]), 0)
        self.assertFalse(res[0]["https://doi.org/10.7892/boris.108387"]["conforms"])
        self.assertEqual(
            len(res[0]["https://doi.org/10.7892/boris.108387"]["errors"]), 2
        )
        self.assertEqual(
            len(res[0]["https://doi.org/10.7892/boris.108387"]["warnings"]), 11
        )

    @unittest.skip("Deprecated, Profile.py should be used instead")
    def test_datacite_validation_kg(self):
        input_url = "https://commons.datacite.org/doi.org/10.7892/boris.108387"
        datacite_md = WebResource(input_url)
        kg = datacite_md.get_rdf()

        print(f"{len(kg)} loaded RDF triples")
        print(kg.serialize(format="turtle"))
        res = validate_any_from_KG(kg=kg)
        self.assertGreater(len(res), 0)
        self.assertFalse(res["https://doi.org/10.7892/boris.108387"]["conforms"])
        self.assertEqual(len(res["https://doi.org/10.7892/boris.108387"]["errors"]), 2)
        self.assertEqual(
            len(res["https://doi.org/10.7892/boris.108387"]["warnings"]), 11
        )

    def test_inrae_dataverse_validation(self):
        res = validate_any_from_microdata(
            input_url="https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ"
        )
        self.assertEqual(len(res[0]), 1)

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
