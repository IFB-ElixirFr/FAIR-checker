import unittest
import requests
import yaml

# from profiles.Profile
from profiles.ProfileFactory import (
    dyn_evaluate_profile_with_conformsto,
    profile_file_parser,
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
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    @classmethod
    def setUp(self):
        """Set up application for testing."""
        github_token = environ.get("GITHUB_TOKEN")

        self.headers = {
            "Authorization": "token {}".format(github_token),
            "User-Agent": "FAIR-checker",
            "Accept": "application/vnd.github.v3+json",
        }

    # def test_gen_SHACL_from_import(self):
    #     self.test_github_rate_limite()
    #     profiles = get_profiles_specs_from_github()
    #     for profile_key in profiles.keys():
    #         print(json.dumps(profiles[profile_key], indent=4))
    #         gen_SHACL_from_profile(
    #             profiles[profile_key]["name"],
    #             "sc:" + profiles[profile_key]["name"],
    #             profiles[profile_key]["min_props"],
    #             profiles[profile_key]["rec_props"],
    #         )

    def test_create_profile_object(self):
        profiles_list = ProfileFactory.create_all_profiles_from_specifications()
        # Bioschemas keeps publishing profiles, and test_update_profiles rewrites
        # profiles/bs_profiles.json in place, so an exact count is not stable.
        self.assertGreaterEqual(len(profiles_list), 32)

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

        self.assertEqual(len(result), 5)

    def test_wfh_type_eval(self):

        url = "https://workflowhub.eu/workflows/18"
        kg = WebResource(url).get_rdf()

        result = evaluate_profile_from_type(kg)

        print(result)

        self.assertGreaterEqual(len(result), 10)

    def test_fairchecker_conformsto_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)
        result = dyn_evaluate_profile_with_conformsto(kg)

        self.assertEqual(
            result["https://github.com/IFB-ElixirFr/FAIR-checker"]["conforms"], True
        )

    def test_fairchecker_type_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)

        issues = evaluate_profile_from_type(kg)
        print(issues)

        # Profiles are matched again now that https://schema.org/ types resolve
        # to the sc: keys the profile table uses; this asserted 0 while that
        # lookup was silently failing.
        self.assertEqual(len(issues), 4)

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
        self.assertGreaterEqual(len(results), 32)

    def test_req_profile_versions(self):
        response = requests.get(
            "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/profile_versions.yaml"
        )
        content = response.text
        dict_content = yaml.safe_load(content)
        print(dict_content)
