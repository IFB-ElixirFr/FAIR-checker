import unittest
import requests
import json
from rdflib import Graph

from metrics.FairCheckerExceptions import (
    BioschemasProfileNotFoundException,
    BioschemasProfileException,
)

from profiles.ProfileFactory import (
    evaluate_profile_from_type,
    evaluate_profile_with_conformsto,
    dyn_evaluate_profile_with_conformsto,
    ProfileFactory,
    Profile,
    PROFILES,
)
from metrics.WebResource import WebResource

PROFILE_URLS = [
    "https://bioschemas.org/profiles/Taxon/0.7-DRAFT",
    "https://bioschemas.org/profiles/Study/0.2-DRAFT",
    "https://bioschemas.org/profiles/ProteinAnnotation/0.6-DRAFT",
    "https://bioschemas.org/profiles/TaxonName/0.1-DRAFT",
    "https://bioschemas.org/profiles/Dataset/0.4-DRAFT",
    "https://bioschemas.org/profiles/Gene/1.0-RELEASE",
    "https://bioschemas.org/profiles/Course/1.0-RELEASE",
    "https://bioschemas.org/profiles/DataCatalog/",
    "https://bioschemas.org/profiles/TrainingMaterial/1.0-RELEASE",
    "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE",
    "https://bioschemas.org/profiles/ComputationalWorkflow/1.0-RELEASE",
    "https://bioschemas.org/profiles/CourseInstance/0.9-DRAFT",
    "https://bioschemas.org/profiles/SequenceRange/0.1-DRAFT",
    "https://bioschemas.org/profiles/ScholarlyArticle/0.2-DRAFT-2020_12_03",
    "https://bioschemas.org/profiles/Disease/0.1-DRAFT",
    "https://bioschemas.org/profiles/Person/0.2-DRAFT-2019_07_19",
    "https://bioschemas.org/profiles/Dataset/0.3-RELEASE-2019_06_14",
    "https://bioschemas.org/profiles/Taxon/0.6-RELEASE",
    "https://bioschemas.org/profiles/CourseInstance/1.0-RELEASE",
    "https://bioschemas.org/profiles/Course/0.10-DRAFT",
    "https://bioschemas.org/profiles/FormalParameter/1.0-RELEASE",
    "https://bioschemas.org/profiles/MolecularEntity/0.5-RELEASE",
    "https://bioschemas.org/profiles/Dataset/1.0-RELEASE",
    "https://bioschemas.org/profiles/Protein/0.12-DRAFT",
]


def gen_urls_for_live_deploys_profiles():
    live_deploys_remote_file = "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/live_deployments.json"
    res = requests.get(live_deploys_remote_file)
    live_deploys = res.json()
    # for r in random.sample(live_deploys["resources"], 5):
    profile_urls = []
    for r in live_deploys["resources"]:
        # print(json.dumps(r, indent=2))
        profile_url_prefix = "https://bioschemas.org/profiles/"
        for p in r["profiles"]:
            profile_url = profile_url_prefix + p["profileName"] + "/" + p["conformsTo"]
            profile_urls.append(profile_url)
    return list(set(profile_urls))


def get_live_deploys_urls():
    results = []
    live_deploys_remote_file = "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/live_deployments.json"
    res = requests.get(live_deploys_remote_file)
    live_deploys = res.json()
    # for r in random.sample(live_deploys["resources"], 5):
    for r in live_deploys["resources"]:
        results.append(r["url"])
    return results


class BioschemasLiveDeploysTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_workflow_without_conformsto(self):
        input_url = "https://workflowhub.eu/workflows/263"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        res = evaluate_profile_from_type(kg)
        print(json.dumps(res, indent=4))

        self.assertEqual(
            len(res["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 3
        )

    def test_workflow_with_conformsto(self):
        input_url = "https://workflowhub.eu/workflows/263"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        res = dyn_evaluate_profile_with_conformsto(kg)
        print(json.dumps(res, indent=4))

        self.assertEqual(
            len(res["https://workflowhub.eu/workflows/263?version=1"]["errors"]), 2
        )

    # Bioschemas profile not found (need handle)
    # https://cells.ebisc.org/BIHi006-D
    @unittest.skip("Bioschemas profile not found (need handle")
    def test_biosample_conformsto(self):
        input_url = "https://cells.ebisc.org/BIHi006-D"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        print(kg.serialize(format="ttl"))
        self.assertGreater(len(kg), 0)
        res = dyn_evaluate_profile_with_conformsto(kg)
        print(json.dumps(res, indent=2))
        self.assertEqual(res["https://cells.ebisc.org/BIHi006-D"]["conforms"], True)
        self.assertEqual(len(res["https://cells.ebisc.org/BIHi006-D"]["errors"]), 0)

    def test_fairchecker_conformsto(self):
        input_url = "https://fair-checker.france-bioinformatique.fr"
        web_resource = WebResource(input_url)
        kg = web_resource.get_rdf()
        self.assertGreater(len(kg), 0)
        res = dyn_evaluate_profile_with_conformsto(kg)
        print(json.dumps(res, indent=2))
        # self.assertEqual(res["https://fair-checker.france-bioinformatique.fr"]["conforms"], True)
        # self.assertEqual(
        #     len(res["https://fair-checker.france-bioinformatique.fr"]["errors"]), 0
        # )

    # TODO add assertions
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

    def test_profile_url_generation(self):
        profiles = gen_urls_for_live_deploys_profiles()
        wrong_urls = []
        correct_urls = []
        for p in profiles:
            print(p)
            response = requests.get(p)
            if response.status_code != 200:
                wrong_urls.append(p)
            else:
                correct_urls.append(p)
        print(f"{len(profiles)} declared profiles in live deploys")
        print(f"{len(correct_urls)} profile urls are ok")
        print(f"{len(wrong_urls)} profile urls are not resolvable")
        print("Correct URLs:")
        print(correct_urls)
        print("Non resolvable profile URLs:")
        print(wrong_urls)

    def test_json_profile_accessibility(self):
        datacat = "https://bioschemas.org/profiles/DataCatalog/"
        gene = "https://bioschemas.org/profiles/Gene/1.0-RELEASE"

        try:
            ProfileFactory.create_profile_from_remote(datacat)
        except BioschemasProfileNotFoundException as error:
            print(error)
            self.assertIsNotNone(error)

        profile_gene = ProfileFactory.create_profile_from_remote(gene)

        self.assertEqual(profile_gene.shape_name, "Gene")
        self.assertEqual(len(profile_gene.min_props), 2)
        self.assertEqual(len(profile_gene.rec_props), 4)
        shape_rdf = profile_gene.get_shacl_shape()
        shape_graph = Graph()
        shape_graph.parse(data=shape_rdf, format="ttl")
        self.assertEqual(len(shape_graph), 26)

    def test_ld_bioschemas_annot(self):
        res = get_live_deploys_urls()
        print(res)
        errors = []
        i = 0
        for r in res:
            if True:
                i += 1
                print("#######" + str(i))
                try:
                    status_code = requests.head(r).status_code
                    print(r)
                    print("Status code: " + str(status_code))
                    kg = WebResource(r).get_rdf()
                    print("Triples: " + str(len(kg)))
                    if not len(kg) > 0:
                        print(f"# Error with {r}")
                        errors.append(r)
                except requests.exceptions.ConnectionError as e:
                    print(e)

        print(f"{len(res)} tested URLS")
        print(f"{len(errors)} failing URLS")
        print(errors)

    def test_uri_invalid(self):
        resource = "https://ebisc.org/"
        kg = WebResource(resource).get_rdf()
        print(len(kg))
        print(kg.serialize(format="json-ld"))
        print(kg.serialize(format="turtle"))

    def test_all(self):
        to_be_skipped = [
            "https://www.proteinatlas.org/",
            "https://enanomapper.github.io/tutorials/",
            "https://www.nanocommons.eu/",
            "https://riskgone.eu/",
            "https://humanmine.org/",
            "https://www.rhea-db.org/",
            "http://www.ebi.ac.uk/pdbe/",
            "https://www.omicsdi.org/",
            "https://ippidb.pasteur.fr/",
            "https://mint.bio.uniroma2.it/",
        ]
        valid_bioschemas = []
        print()
        live_deploys_remote_file = "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/live_deployments.json"
        res = requests.get(live_deploys_remote_file)
        live_deploys = res.json()
        # for r in random.sample(live_deploys["resources"], 5):
        for r in live_deploys["resources"]:
            print(r["url"])
            if not r["url"] in to_be_skipped:
                try:
                    web_resource = WebResource(r["url"])
                    kg = web_resource.get_rdf()
                    try:
                        validation_res = dyn_evaluate_profile_with_conformsto(kg)
                        for k in validation_res.keys():
                            if validation_res[k]["conforms"]:
                                print(f"VALID Bioschemas markup for {k}")
                                valid_bioschemas.append(validation_res[k])
                            else:
                                print(validation_res[k])
                    except BioschemasProfileException as error:
                        print(error)
                except Exception as error:
                    print(error)
                    to_be_skipped.append(r["url"])
        print(to_be_skipped)


if __name__ == "__main__":
    unittest.main()
