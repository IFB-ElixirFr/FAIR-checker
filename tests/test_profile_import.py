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
        print(response.json())


    @unittest.skip("Need github TOKEN key to work")
    def test_import_bs_specs(self):
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
                                        releases[res["download_url"]] = m.group(1)
                                        # releases[m.group(1)] = res["download_url"]
                                    elif "DRAFT" in res["download_url"]:
                                        drafts[res["download_url"]] = m.group(1)

                                    response = requests.get(res["download_url"], headers=self.headers)
                                    jsonld = response.json()
                                    profile_dict = {
                                        "name": profile_name,
                                        "file": res["download_url"],
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

                            

                            if releases:
                                # print(releases.keys())
                                print(releases.values())
                                # sort_orders = sorted(releases.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()
                            else:
                                # print(drafts.keys())
                                print(drafts.values())
                                # sort_orders = sorted(drafts.items(), key=lambda x: x[1], reverse=True)
                                # sort_orders.values()




                # if i > 20:
                #     break
            # print(profiles_list)

        else:
            print('Content was not found.')