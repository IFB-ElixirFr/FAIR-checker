from contextlib import AbstractAsyncContextManager
import unittest

from rich.console import Console
from rich.table import Table
from rich.text import Text

from rdflib import ConjunctiveGraph, URIRef

from profiles.bioschemas_shape_gen import gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import gen_SHACL_from_target_class
from profiles.bioschemas_shape_gen import validate_shape_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_RDF
from profiles.bioschemas_shape_gen import validate_any_from_KG
from profiles.bioschemas_shape_gen import validate_any_from_microdata
from profiles.bioschemas_shape_gen import validate_shape_from_microdata

from profiles.Profile import Profile
from profiles.ProfileFactory import ProfileFactory

from metrics.WebResource import WebResource

import requests
import re

# from app import app
# from flask import current_app

# from requests.packages.urllib3.util.ssl_ import create_urllib3_context
# create_urllib3_context()


class ImportBSProfileTestCase(unittest.TestCase):

    def setUp(self):
        """Set up application for testing."""
        github_token = ""

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



    @unittest.skip("Need github TOKEN key to work")
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
                                if res["type"] == "file" and not "DEPRECATED" in res["download_url"]:

                                    # print(res["download_url"])
                                    regex_version = "_v([0-9]*.[0-9]*)-"
                                    m = re.search(regex_version, res["download_url"])
                                    # print(m.group(1))
                                    # # print(m.group(1).split("."))
                                    # print(m.group(2))
                                    
                                    if "RELEASE" in res["download_url"]:
                                        releases[res["download_url"]] = float(m.group(1))
                                        # releases[m.group(1)] = res["download_url"]
                                    elif "DRAFT" in res["download_url"]:
                                        drafts[res["download_url"]] = float(m.group(1))



                            
                            url_profile = ""
                            if releases:
                                # print(releases.keys())
                                print("Releases: ")
                                print(releases.values())
                                if releases.values():
                                    latest_rel = max(releases.values())
                                    print(latest_rel)
                                    print("Release Key value: ", list(releases.keys())[list(releases.values()).index(latest_rel)])
                                    print("Release Key value: ", [k for k, v in releases.items() if v == latest_rel])
                                url_profile = list(releases.keys())[list(releases.values()).index(latest_rel)]
                                # sort_orders = sorted(releases.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()
                            else:
                                print("Drafts: ")
                                # print(drafts.keys())
                                print(drafts.values())
                                if drafts.values():
                                    latest_rel = max(drafts.values())
                                    print(latest_rel)
                                    print("Draft Key value: ", list(drafts.keys())[list(drafts.values()).index(latest_rel)])
                                    print("Draft Key value: ", [k for k, v in drafts.items() if v == latest_rel])
                                    url_profile = list(drafts.keys())[list(drafts.values()).index(latest_rel)]
                                # sort_orders = sorted(drafts.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()

                            if url_profile:
                                response = requests.get(url_profile, headers=self.headers)
                                jsonld = response.json()
                                profile_dict = {
                                    "name": profile_name,
                                    "file": url_profile,
                                    "required": [],
                                    "recommended": [],
                                    "optional": [],
                                }

                                if "required" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["required"] = jsonld["@graph"][0]["$validation"]["required"]
                                if "recommended" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["recommended"] = jsonld["@graph"][0]["$validation"]["recommended"]
                                if "optional" in jsonld["@graph"][0]["$validation"]:
                                    profile_dict["optional"] = jsonld["@graph"][0]["$validation"]["optional"]

                                profiles_list.append(profile_dict)




                # if i > 20:
                #     break
            print(profiles_list)

        else:
            print('Content was not found.')