from logging import warning
import unittest

from profiles.bioschemas_shape_gen import gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import gen_SHACL_from_target_class
from profiles.bioschemas_shape_gen import validate_shape_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_microdata
from profiles.bioschemas_shape_gen import validate_shape_from_microdata

from metrics.WebResource import WebResource


class GenSHACLTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

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
        shape = gen_SHACL_from_target_class(target_class=target_class)
        self.assertTrue("sh:path" in shape)

    def test_any_resource(self):

        # todo assertions on error count for each test
        res = validate_any_from_RDF(
            input_url="https://bio.tools/api/jaspar?format=jsonld", rdf_syntax="json-ld"
        )
        self.assertGreater(len(res), 0)
        self.assertEquals(len(res["https://bio.tools/jaspar"]["warnings"]), 5)
        self.assertEquals(len(res["https://bio.tools/jaspar"]["errors"]), 3)

        # self.assertTrue(res["conforms"])

        # todo assertions : no errors
        res = validate_any_from_microdata(
            input_url="https://doi.pangaea.de/10.1594/PANGAEA.914331"
        )
        self.assertGreater(len(res), 0)
        self.assertTrue(res["https://doi.org/10.1594/PANGAEA.914331"]["conforms"])

        res = validate_any_from_microdata(
            input_url="https://search.datacite.org/works/10.7892/boris.108387"
        )
        self.assertGreater(len(res), 0)
        self.assertFalse(res["https://doi.org/10.7892/boris.108387"]["conforms"])
        self.assertEquals(len(res["https://doi.org/10.7892/boris.108387"]["errors"]), 2)
        self.assertEquals(
            len(res["https://doi.org/10.7892/boris.108387"]["warnings"]), 11
        )

        res = validate_any_from_microdata(
            input_url="https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ"
        )
        self.assertGreater(len(res), 0)


if __name__ == "__main__":
    unittest.main()
