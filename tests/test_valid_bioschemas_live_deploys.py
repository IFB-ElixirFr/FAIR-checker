import unittest
import requests
import random
import json

from profiles.ProfileFactory import (
    evaluate_profile_from_type,
    evaluate_profile_with_conformsto,
)
from metrics.WebResource import WebResource


class BioschemasLiveDeploysTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_workflow_validation(self):
        input_url = "https://workflowhub.eu/workflows/263"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        res = evaluate_profile_from_type(kg)
        print(json.dumps(res, indent=4))

        self.assertEqual(
            len(res["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 2
        )

    def test_workflow_conformsto(self):
        input_url = "https://workflowhub.eu/workflows/263"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        res = evaluate_profile_from_conformsto(kg)
        print(json.dumps(res, indent=4))

        self.assertEqual(
            len(res["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 2
        )

    # https://cells.ebisc.org/BIHi006-D
    def test_biosample_conformsto(self):
        input_url = "https://cells.ebisc.org/BIHi006-D"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        print(kg.serialize(format="ttl"))
        self.assertGreater(len(kg), 0)
        res = evaluate_profile_with_conformsto(kg)
        print(json.dumps(res, indent=2))
        self.assertEqual(res["conforms"], True)
        self.assertEqual(len(res["https://cells.ebisc.org/BIHi006-D"]["errors"]), 0)

    def test_fairchecker_conformsto(self):
        input_url = "https://fair-checker.france-bioinformatique.fr"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        self.assertGreater(len(kg), 0)
        res = evaluate_profile_with_conformsto(kg)
        print(json.dumps(res, indent=2))
        self.assertEqual(res["conforms"], True)
        self.assertEqual(
            len(res["https://fair-checker.france-bioinformatique.fr"]["errors"]), 0
        )

    def test_fairchecker_type(self):
        input_url = "https://fair-checker.france-bioinformatique.fr"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        self.assertGreater(len(kg), 0)
        res = evaluate_profile_from_type(kg)
        print(json.dumps(res, indent=2))
        # self.assertEqual(res["conforms"], "true")
        # self.assertEqual(
        #     len(res["https://fair-checker.france-bioinformatique.fr"]["errors"]), 0
        # )

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
