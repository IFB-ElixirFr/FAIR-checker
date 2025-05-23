import unittest
import requests
import json
import yaml
from rdflib import ConjunctiveGraph

from profiles.bioschemas_shape_gen import get_profiles_specs_from_github
from profiles.bioschemas_shape_gen import gen_SHACL_from_profile

# from profiles.Profile
from profiles.ProfileFactory import (
    dyn_evaluate_profile_with_conformsto,
    profile_file_parser,
    load_profiles,
    update_profiles,
    evaluate_profile_from_type,
)

from profiles.ProfileFactory import ProfileFactory

from os import environ, path
from dotenv import load_dotenv

from metrics.WebResource import WebResource


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

# from app import app
# from flask import current_app

# from requests.packages.urllib3.util.ssl_ import create_urllib3_context
# create_urllib3_context()


class ImportBSProfileTestCase(unittest.TestCase):
    def setUp(self):
        """Set up application for testing."""
        github_token = environ.get("GITHUB_TOKEN")

        self.headers = {
            "Authorization": "token {}".format(github_token),
            "User-Agent": "FAIR-checker",
            "Accept": "application/vnd.github.v3+json",
        }

    @unittest.skip("Need github TOKEN key to work")
    def test_github_rate_limite(self):
        url = "https://api.github.com/rate_limit"
        response = requests.get(url, headers=self.headers)
        print("Remaining: " + str(response.json()["resources"]["core"]["remaining"]))

    @unittest.skip("Doesn't work on github action, need to fix")
    def test_namespace_SequenceAnnotation(self):
        gh_profile_url = "https://raw.githubusercontent.com/BioSchemas/specifications/master/SequenceAnnotation/jsonld/SequenceAnnotation_v0.7-DRAFT.json"
        response = requests.get(gh_profile_url, headers=self.headers)
        jsonld = response.json()
        kg = ConjunctiveGraph()
        kg.parse(data=jsonld, format="json-ld")
        print(len(kg))

    @unittest.skip("Need github TOKEN key to work")
    def test_import_bs_specifications(self):
        self.test_github_rate_limite()
        profiles = get_profiles_specs_from_github()
        self.test_github_rate_limite()
        self.assertEqual(31, len(profiles))

        for profile in profiles:
            print(json.dumps(profile, indent=2))

    def test_gen_SHACL_from_import(self):
        self.test_github_rate_limite()
        profiles = get_profiles_specs_from_github()
        for profile_key in profiles.keys():
            print(json.dumps(profiles[profile_key], indent=4))
            gen_SHACL_from_profile(
                profiles[profile_key]["name"],
                "sc:" + profiles[profile_key]["name"],
                profiles[profile_key]["min_props"],
                profiles[profile_key]["rec_props"],
            )

    def test_load_profiles(self):
        self.test_github_rate_limite()
        profiles = load_profiles()
        self.assertEqual(31, len(profiles))

    def test_create_profile_object(self):
        profiles_list = ProfileFactory.create_all_profiles_from_specifications()
        self.assertEqual(31, len(profiles_list))

    def test_update_profiles(self):
        update_profiles()

    def test_ref_profiles(self):
        profiles_dict = ProfileFactory.create_all_profiles_from_specifications()
        for profile_k in profiles_dict.keys():
            ref_profile = profiles_dict[profile_k].get_ref_profile()
            response = requests.head(ref_profile, verify=False, timeout=5)
            print(ref_profile)
            print(response.status_code)
            # self.assertEqual(response.status_code, 200)

    def test_profile_get_name(self):
        profiles_dict = ProfileFactory.create_all_profiles_from_specifications()
        for profile_k in profiles_dict.keys():
            print(profiles_dict[profile_k])

    def test_wfh_conformsto_eval(self):
        url = "https://workflowhub.eu/workflows/18"
        kg = WebResource(url).get_rdf()

        self.assertGreater(len(kg), 49)
        result = dyn_evaluate_profile_with_conformsto(kg)

        self.assertEqual(len(result), 1)

    def test_wfh_type_eval(self):

        url = "https://workflowhub.eu/workflows/18"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 49)

        result = evaluate_profile_from_type(kg)

        print(result)

        self.assertEqual(len(result), 11)

    def test_fairchecker_conformsto_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)
        result = dyn_evaluate_profile_with_conformsto(kg)
        print(json.dumps(result, indent=True))

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result["https://github.com/IFB-ElixirFr/FAIR-checker"]["conforms"], True
        )

    def test_fairchecker_type_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)

        result = evaluate_profile_from_type(kg)
        print(result)

        self.assertEqual(len(result), 4)
        self.assertFalse(result["https://orcid.org/0000-0002-3597-8557"]["conforms"])

    def test_profile_file_parser(self):

        url_profiles = [
            "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemas.json",
            "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemasdrafts.json",
            "https://raw.githubusercontent.com/BioSchemas/specifications/master/Gene/jsonld/Gene_v0.3-DRAFT-2018_08_21.json",
            "https://raw.githubusercontent.com/BioSchemas/specifications/master/ComputationalWorkflow/jsonld/ComputationalWorkflow_v1.0-RELEASE.json",
        ]

        results = {}
        profiles_names_list = []
        for url_profile in url_profiles:
            profiles_dict = profile_file_parser(url_profile)

            for profile_key in profiles_dict:
                if profiles_dict[profile_key]["name"] not in profiles_names_list:
                    results[profile_key] = profiles_dict[profile_key]
                    profiles_names_list.append(profiles_dict[profile_key]["name"])
        self.assertEqual(len(results), 31)

    def test_req_profile_versions(self):
        response = requests.get(
            "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/profile_versions.yaml"
        )
        content = response.text
        dict_content = yaml.safe_load(content)
        print(dict_content)
