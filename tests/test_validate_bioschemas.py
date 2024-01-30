import unittest
from app import app
from rdflib import ConjunctiveGraph
from metrics.WebResource import WebResource
from profiles.Profile import Profile
from profiles.ProfileFactory import (
    find_conformsto_subkg,
    dyn_evaluate_profile_with_conformsto,
    evaluate_profile_from_type,
)


class ValidateBioschemasTestCase(unittest.TestCase):
    uri_wf = "https://workflowhub.eu/workflows/18"
    uri_tool = "https://bio.tools/bwa"
    uri_dataset = "https://doi.pangaea.de/10.1594/PANGAEA.914331"

    def setUp(self):
        app.config["ENV"] = "test"
        # app.config['TESTING'] = True
        app.config.from_object("config.TestingConfig")
        self.app = app.test_client()

    @unittest.skip("Temporary disabled because doesn't work in GH actions")
    def test_validate_biotools(self):
        response = self.app.get("/validate_bioschemas?uri=" + self.uri_tool)
        self.assertEqual(200, response.status_code)
        # self.assertEqual(24095, len(response.get_data()))

    @unittest.skip("Temporary disabled because doesn't work in GH actions")
    def test_validate_wfh(self):
        response = self.app.get("/validate_bioschemas?uri=" + self.uri_wf)
        self.assertEqual(200, response.status_code)
        # self.assertEqual(22111, len(response.get_data()))

    def test_find_conformsto(self):
        wr_kg = WebResource(self.uri_tool).get_rdf()
        sub_kg_list = find_conformsto_subkg(wr_kg)

        self.assertEqual(len(sub_kg_list), 1)
        for sub_kg in sub_kg_list:
            print(len(sub_kg["sub_kg"]))

    def test_named_graph(self):
        wr_kg = WebResource(self.uri_wf).get_rdf()
        # validation_ct = dyn_evaluate_profile_with_conformsto(wr_kg)
        validation_type = evaluate_profile_from_type(wr_kg)

        # print(validation_ct)
        print(validation_type)

    def test_custom_profiles_http_schema(self):
        my_metadata = """
@prefix ns: <http://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://my_resource>    rdf:type <http://TestClass> ;
                        ns:title "Title" ;
                        ns:identifier "NS:ID" ;
                        <http://schema.org/author> "Bla" ; 
                        ns:license "MIT" .
        """

        # kg = WebResource(self.uri_tool).get_rdf()
        kg = ConjunctiveGraph()
        kg.parse(data=my_metadata, format="turtle")
        print(kg.serialize(format="turtle"))

        min_props = ["<http://schema.org/title>"]
        rec_props = ["<http://schema.org/identifier>", "<http://schema.org/author>"]
        target_classes = ["<http://TestClass>"]

        p = Profile(
            shape_name="test",
            target_classes=target_classes,
            min_props=min_props,
            rec_props=rec_props,
            ref_profile=None,
        )

        shape = p.get_shacl_shape()
        print(shape)

        conforms, warnings, errors = p.validate_shape(kg, shape)

        conforms = len(errors) == 0
        results = {
            "conforms": conforms,
            "warnings": warnings,
            "errors": errors,
        }
        print(results)
        self.assertEquals(True, conforms)
        self.assertEquals(0, len(warnings))
        self.assertEquals(0, len(errors))

    def test_custom_profiles_https_schema(self):
        my_metadata = """
@prefix ns: <https://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://my_resource>    rdf:type <http://TestClass> ;
                        ns:title "Title" ;
                        ns:identifier "NS:ID" ;
                        ns:license "MIT" .
        """

        # kg = WebResource(self.uri_tool).get_rdf()
        kg = ConjunctiveGraph()
        kg.parse(data=my_metadata, format="turtle")
        print(kg.serialize(format="turtle"))

        min_props = ["<https://schema.org/title>"]
        rec_props = ["<https://schema.org/identifier>"]
        target_classes = ["<http://TestClass>"]

        p = Profile(
            shape_name="test",
            target_classes=target_classes,
            min_props=min_props,
            rec_props=rec_props,
            ref_profile=None,
        )

        shape = p.get_shacl_shape()
        print(shape)

        conforms, warnings, errors = p.validate_shape(kg, shape)

        conforms = len(errors) == 0
        results = {
            "conforms": conforms,
            "warnings": warnings,
            "errors": errors,
        }
        print(results)
        self.assertEquals(True, conforms)
        self.assertEquals(0, len(warnings))
        self.assertEquals(0, len(errors))
