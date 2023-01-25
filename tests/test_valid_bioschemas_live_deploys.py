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

import requests
import random


class BioschemasLiveDeploysTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_workflow_validation(self):
        res = validate_any_from_microdata(
            input_url="https://workflowhub.eu/workflows/263"
        )
        self.assertEqual(
            len(res[0]["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 4
        )

    def test_all(self):
        to_be_skipped = [
            "https://www.proteinatlas.org/",
            "https://enanomapper.github.io/tutorials/",
            "https://www.nanocommons.eu/",
            "https://riskgone.eu/",
            "https://humanmine.org/",
            "https://www.rhea-db.org/",
            "http://www.ebi.ac.uk/pdbe/",
        ]
        valid_bioschemas = []
        print()
        live_deploys_remote_file = "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/live_deployments.json"
        res = requests.get(live_deploys_remote_file)
        live_deploys = res.json()
        for r in random.sample(live_deploys["resources"], 5):
            print(r["url"])
            if not r["url"] in to_be_skipped:
                validation_res, kg = validate_any_from_microdata(r["url"])
                for k in validation_res.keys():
                    if validation_res[k]["conforms"]:
                        print(f"VALID Bioschemas markup for {k}")
                        valid_bioschemas.append(validation_res[k])
                    else:
                        print(validation_res[k])
        print("valid_bioschemas")


if __name__ == "__main__":
    unittest.main()
