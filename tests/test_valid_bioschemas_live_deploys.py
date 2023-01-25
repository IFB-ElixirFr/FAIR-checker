import unittest
import requests
import random
import cProfile
from pstats import Stats, SortKey

from profiles.ProfileFactory import (
    evaluate_profile_from_type,
    evaluate_profile_from_conformsto,
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
        print(input_url)
        web_resource = WebResource(input_url)
        print(f"fetching {input_url}")
        kg = web_resource.get_rdf()
        print(f"got {len(kg)} triples")
        res = evaluate_profile_from_type(kg)
        print(f"bioschemas validation results : ")
        print()
        print(res)
        print()
        # self.assertEqual(
        #     len(res[0]["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 4
        # )

    def test_workflow_conformsto(self):
        input_url = "https://workflowhub.eu/workflows/263"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        res = evaluate_profile_from_conformsto(kg)
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
    do_profiling = True
    if do_profiling:
        with cProfile.Profile() as pr:
            unittest.main()
        with open("profiling_stats.txt", "w") as stream:
            stats = Stats(pr, stream=stream)
            stats.strip_dirs()
            stats.sort_stats("time")
            stats.dump_stats(".prof_stats")
            stats.print_stats()
    else:
        unittest.main()
