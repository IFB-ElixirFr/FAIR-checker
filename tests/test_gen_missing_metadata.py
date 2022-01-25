import unittest
import rdflib

import metrics.util as util
from metrics.WebResource import WebResource


class MissingMetadataTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_url(self):
        self.assertFalse(
            util.is_URL("qsd jqshgd"), "This is not an URL, result should be False"
        )
        self.assertTrue(
            util.is_URL("http://bio.tools/edam"),
            "This is a valid URL, result should be True",
        )

    def test_something(self):

        data = {
            "err": {
                "http://schema.org/applicationCategory": "my_Category",
            },
            "warn": {
                "http://schema.org/applicationCategory": "",
                "http://schema.org/author": "qskjdh qskjd",
                "http://schema.org/softwareVersion": "1.23",
                "http://schema.org/featureList": "http://bio.tools/my_feature",
                "http://schema.org/applicationSubCategory": "",
            },
            "url": "https://bio.tools/bwa",
        }

        new_kg = rdflib.ConjunctiveGraph()

        # TODO check that url is well formed
        if util.is_URL(data["url"]):
            uri = rdflib.URIRef(data["url"])

            for p in data["warn"].keys():
                if data["warn"][p]:
                    value = data["warn"][p]
                    if util.is_URL(value):
                        new_kg.add((uri, rdflib.URIRef(p), rdflib.URIRef(value)))
                    else:
                        new_kg.add((uri, rdflib.URIRef(p), rdflib.Literal(value)))

            for p in data["err"].keys():
                if data["err"][p]:
                    value = data["err"][p]
                    if util.is_URL(value):
                        new_kg.add((uri, rdflib.URIRef(p), rdflib.URIRef(value)))
                    else:
                        new_kg.add((uri, rdflib.URIRef(p), rdflib.Literal(value)))

            print("****** Turtle syntax *****")
            print(new_kg.serialize(format="turtle"))
            print("**************************")

            print("***** JSON-LD syntax *****")
            print(new_kg.serialize(format="json-ld"))
            print("**************************")

        self.assertEqual(len(new_kg), 4)


if __name__ == "__main__":
    unittest.main()
