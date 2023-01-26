import unittest
import requests
import re
import json
import yaml
from rdflib import ConjunctiveGraph

from profiles.bioschemas_shape_gen import get_profiles_specs_from_github
from profiles.bioschemas_shape_gen import gen_SHACL_from_profile
# from profiles.Profile 
from profiles.ProfileFactory import load_profiles, evaluate_profile_with_conformsto, evaluate_profile_from_type

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

    # @unittest.skip("Need github TOKEN key to work")
    def test_github_rate_limite(self):
        url = "https://api.github.com/rate_limit"
        response = requests.get(url, headers=self.headers)
        print("Remaining: " + str(response.json()["resources"]["core"]["remaining"]))

    def test_namespace_SequenceAnnotation(self):
        gh_profile_url = "https://raw.githubusercontent.com/BioSchemas/specifications/master/SequenceAnnotation/jsonld/SequenceAnnotation_v0.7-DRAFT.json"
        response = requests.get(gh_profile_url, headers=self.headers)
        jsonld = response.json()
        kg = ConjunctiveGraph()
        kg.parse(data=jsonld, format="json-ld")
        print(len(kg))

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
        print(json.dumps(profiles, indent=4))
        print(len(profiles))
        for profile_key in profiles.keys():
            ref_profile = profiles[profile_key]["ref_profile"]
            response = requests.head(ref_profile, verify=False, timeout=5)

            # self.assertEqual(response.status_code, 200)

            gen_SHACL_from_profile(
                profiles[profile_key]["name"],
                "sc:" + profiles[profile_key]["name"],
                profiles[profile_key]["min_props"],
                profiles[profile_key]["rec_props"],
            )

    def test_wfh_conformsto_eval(self):
        url = "https://workflowhub.eu/workflows/18"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 49)
        result = evaluate_profile_with_conformsto(kg)

        self.assertEqual(len(result), 1)

    def test_wfh_type_eval(self):
        url = "https://workflowhub.eu/workflows/18"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 49)
        result = evaluate_profile_from_type(kg)

        self.assertEqual(len(result), 11)

    def test_fairchecker_conformsto_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)
        result = evaluate_profile_with_conformsto(kg)

        self.assertEqual(len(result), 0)

    def test_fairchecker_type_eval(self):
        url = "https://fair-checker.france-bioinformatique.fr/"
        kg = WebResource(url).get_rdf()

        self.assertEqual(len(kg), 35)

        result = evaluate_profile_from_type(kg)

        self.assertEqual(len(result), 3)



    def test_req_profile_versions(self):
        response = requests.get("https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/profile_versions.yaml")
        content = response.text 
        dict_content = yaml.safe_load(content)
        print(dict_content)





    # @unittest.skip("Need github TOKEN key to work")
    def test_import_bs_specs(self):
        self.test_github_rate_limite()
        url = "https://api.github.com/repos/BioSchemas/specifications/contents"
        # with self.test_app.app_context():
        #     print(current_app.config)
        #     github_token = current_app.config["GITHUB_TOKEN"]

        response = requests.get(url, headers=self.headers)

        print(response.status_code)
        i = 0

        profiles_list = []

        if response.status_code == requests.codes.ok:
            profiles_list = []
            results_json = response.json()  # the response is a JSON
            # req is now a dict with keys: name, encoding, url, size ...
            # and content. But it is encoded with base64.
            for result in results_json:
                i += 1

                if result["type"] == "dir":

                    profile_name = result["name"]
                    print(profile_name)

                    response = requests.get(result["url"], headers=self.headers)

                    results_json = response.json()
                    for result in results_json:

                        if result["name"] == "jsonld":
                            response = requests.get(result["url"], headers=self.headers)
                            results_json = response.json()
                            releases = {}
                            drafts = {}
                            for res in results_json:
                                if (
                                    res["type"] == "file"
                                    and not "DEPRECATED" in res["download_url"]
                                ):

                                    # print(res["download_url"])
                                    regex_version = "_v([0-9]*.[0-9]*)-"
                                    m = re.search(regex_version, res["download_url"])
                                    # print(m.group(1))
                                    # # print(m.group(1).split("."))
                                    # print(m.group(2))

                                    if "RELEASE" in res["download_url"]:
                                        releases[res["download_url"]] = float(
                                            m.group(1)
                                        )
                                        # releases[m.group(1)] = res["download_url"]
                                    elif "DRAFT" in res["download_url"]:
                                        drafts[res["download_url"]] = float(m.group(1))

                            latest_url_dl = ""
                            if releases:
                                # print(releases.keys())
                                print("Releases: ")
                                print(releases.values())
                                if releases.values():
                                    latest_rel = max(releases.values())
                                    print(latest_rel)
                                    print(
                                        "Release Key value: ",
                                        list(releases.keys())[
                                            list(releases.values()).index(latest_rel)
                                        ],
                                    )
                                    print(
                                        "Release Key value: ",
                                        [
                                            k
                                            for k, v in releases.items()
                                            if v == latest_rel
                                        ],
                                    )
                                latest_url_dl = list(releases.keys())[
                                    list(releases.values()).index(latest_rel)
                                ]
                                # sort_orders = sorted(releases.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()
                            else:
                                print("Drafts: ")
                                # print(drafts.keys())
                                print(drafts.values())
                                if drafts.values():
                                    latest_rel = max(drafts.values())
                                    print(latest_rel)
                                    print(
                                        "Draft Key value: ",
                                        list(drafts.keys())[
                                            list(drafts.values()).index(latest_rel)
                                        ],
                                    )
                                    print(
                                        "Draft Key value: ",
                                        [
                                            k
                                            for k, v in drafts.items()
                                            if v == latest_rel
                                        ],
                                    )
                                    latest_url_dl = list(drafts.keys())[
                                        list(drafts.values()).index(latest_rel)
                                    ]
                                # sort_orders = sorted(drafts.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()

                            if latest_url_dl:
                                response = requests.get(
                                    latest_url_dl, headers=self.headers
                                )
                                jsonld = response.json()
                                profile_dict = {
                                    "name": profile_name,
                                    "file": latest_url_dl,
                                    "required": [],
                                    "recommended": [],
                                    "optional": [],
                                }

                                if "required" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["required"] = jsonld["@graph"][0][
                                        "$validation"
                                    ]["required"]
                                if "recommended" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["recommended"] = jsonld["@graph"][0][
                                        "$validation"
                                    ]["recommended"]
                                if "optional" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["optional"] = jsonld["@graph"][0][
                                        "$validation"
                                    ]["optional"]

                                profiles_list.append(profile_dict)

                # if i > 20:
                #     break
            print(profiles_list)

        else:
            print("Content was not found.")
