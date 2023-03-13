from profiles.Profile import Profile
from metrics.FairCheckerExceptions import BioschemasProfileNotFoundException
from os import environ, path
import requests
import re
import json
import os
import yaml
from tqdm import tqdm
from rdflib import URIRef, ConjunctiveGraph
from rdflib.namespace import RDF

# from app import dev_logger


def profile_file_parser(url_profile):
    response = requests.get(url_profile)
    if response.status_code == 200:
        profiles_dict = {}
        profiles_jsonld = response.json()

        for element in profiles_jsonld["@graph"]:
            profile_dict = {
                "name": "",
                "target_classes": [],
                "file": "",
                "required": [],
                "recommended": [],
                "optional": [],
                "id": "",
                "ref_profile": "",
            }
            profiles_versions = request_profile_versions()

            # for element in profiles_jsonld["@graph"]:
            if element["@type"] == "rdfs:Class":
                # print("Class: " + element["@id"])
                name = element["rdfs:label"]
                profile_dict["id"] = element["@id"].replace("bioschemas", "bsc")
                profile_dict["name"] = name

                sc_type = element["rdfs:subClassOf"]["@id"]

                # replace DDE prefix by schema.org prefix for Schema.org types
                replace_prefix = {
                    "bioschemastypes:": "sc:",
                    # "bioschemastypesdrafts:": "sc:",
                    "schema:": "sc:",
                }
                for i, j in replace_prefix.items():
                    sc_type = sc_type.replace(i, j)

                profile_dict["target_classes"].append(sc_type)
                if "schema:schemaVersion" in element.keys():
                    for url in element["schema:schemaVersion"]:
                        if "https://bioschemas.org" in url:
                            profile_dict["ref_profile"] = url

                            status_code = requests.head(url).status_code
                            if status_code != 200:
                                print(url)
                                # print(status_code)
                        else:
                            raw_file_base = "https://raw.githubusercontent.com/BioSchemas/specifications/master/"
                            file_url = url
                            file_url_path = file_url.split("/master/")[-1]
                            raw_file_url = raw_file_base + file_url_path
                            profile_dict["file"] = raw_file_url

                            # status_code = requests.head(raw_file_url).status_code
                            # if status_code != 200:
                            print(raw_file_url)
                            # print(status_code)
                else:
                    if profiles_versions[name]["latest_release"]:
                        latest_version = profiles_versions[name]["latest_release"]
                    else:
                        latest_version = profiles_versions[name]["latest_publication"]

                    bs_profile_url_base = (
                        "https://bioschemas.org/profiles/" + name + "/"
                    )
                    bs_profile_url_path = bs_profile_url_base + latest_version
                    # bs_profile_url_path = bs_profile_url_base + url_dl.split("/")[-1].replace("_v", "/").strip(".json")
                    profile_dict["ref_profile"] = bs_profile_url_path
                    # r = requests.head(bs_profile_url_path, verify=False, timeout=5) # it is faster to only request the header
                    # print(r.status_code)

                importance_levels = ["required", "recommended", "optional"]

                for importance in importance_levels:
                    if "$validation" in element:
                        if importance in element["$validation"]:
                            for property in element["$validation"][importance]:

                                added = False
                                # Identifying non Schema properties
                                for elem in profiles_jsonld["@graph"]:
                                    if (
                                        elem["@type"] == "rdf:Property"
                                        and property == elem["rdfs:label"]
                                    ):

                                        profile_dict[importance].append(
                                            # Maybe change prefix in shape gen instead
                                            elem["@id"].replace("bioschemas:", "bsc:")
                                        )
                                        added = True
                                if added:
                                    continue
                                profile_dict[importance].append("sc:" + property)

                profiles_dict[profile_dict["ref_profile"]] = profile_dict

    # for compatibility with existing code
    # profile_dict["min_props"] = profile_dict.pop("required")
    # profile_dict["rec_props"] = profile_dict.pop("recommended")

    # print(json.dumps(profiles_dict, indent=2))
    # print(len(profiles_dict))
    return profiles_dict


def get_profiles_from_dde():
    url_profiles = [
        "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemas.json",
        "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemasdrafts.json",
        # "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemastypes.json",
        # "https://raw.githubusercontent.com/BioSchemas/bioschemas-dde/main/bioschemastypesdrafts.json"
    ]
    results = {}
    profiles_names_list = []
    for url_profile in url_profiles:
        profiles_dict = profile_file_parser(url_profile)

        for profile_key in profiles_dict:
            if profiles_dict[profile_key]["name"] not in profiles_names_list:
                results[profile_key] = profiles_dict[profile_key]
                profiles_names_list.append(profiles_dict[profile_key]["name"])
    return results


@DeprecationWarning
def get_profiles_specs_from_github():
    github_token = environ.get("GITHUB_TOKEN")
    headers = {
        "Authorization": "token {}".format(github_token),
        "User-Agent": "FAIR-checker",
        "Accept": "application/vnd.github.v3+json",
    }
    url = "https://api.github.com/repos/BioSchemas/specifications/contents"

    # Request specifications github
    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        profiles_dict = {}
        profile_folders_json = response.json()

        # Loop over each folder (one folder == one profile and/or one type)
        for profile_folder in profile_folders_json:
            if profile_folder["type"] == "dir":
                profile_name = profile_folder["name"]
                response = requests.get(profile_folder["url"], headers=headers)
                items = response.json()

                # For each profile and/or type, look for jsonld folder
                for item in items:
                    if item["name"] == "jsonld":
                        response = requests.get(item["url"], headers=headers)
                        results_files = response.json()
                        releases = {}
                        drafts = {}
                        # Look for each profile file in json folder and store version and download link for each
                        for file in results_files:
                            if (
                                file["type"] == "file"
                                and "DEPRECATED" not in file["download_url"]
                            ):
                                regex_version = "_v([0-9]*.[0-9]*)-"
                                m = re.search(regex_version, file["download_url"])

                                if "RELEASE" in file["download_url"]:
                                    releases[file["download_url"]] = float(m.group(1))
                                    # releases[m.group(1)] = res["download_url"]
                                # elif "DRAFT" in file["download_url"]:
                                elif "DRAFT" in file["download_url"]:
                                    drafts[file["download_url"]] = float(m.group(1))

                        latest_url_dl = ""
                        if releases:
                            latest_url_dl = get_latest_profile(releases)
                        elif drafts:
                            latest_url_dl = get_latest_profile(drafts)

                        if latest_url_dl:
                            profile_dict = profile_file_parser(latest_url_dl)
                            for profile_k in profile_dict.keys():
                                profiles_dict[
                                    profile_dict[profile_k]["ref_profile"]
                                ] = profile_dict[profile_k]

                        # To get all profiles and not only latest

                        # all_urls = list(releases.keys()) + list(drafts.keys())
                        # print(all_urls)
                        # print(len(all_urls))

                        # for url in all_urls:
                        #     response = requests.get(url, headers=headers)
                        #     jsonld = response.json()
                        #     profile_dict = parse_profile(jsonld, url)
                        #     profiles_dict[profile_dict["ref_profile"]] = profile_dict
        return profiles_dict
    else:
        return False


@DeprecationWarning
def get_latest_profile(profiles_dict):

    latest_rel = max(profiles_dict.values())

    # latest_url_dl = list(profiles_dict.keys())[list(profiles_dict.values()).index(latest_rel)]
    latest_url_dl = [k for k, v in profiles_dict.items() if v == latest_rel]
    return latest_url_dl[0]


def request_profile_versions():
    response = requests.get(
        "https://raw.githubusercontent.com/BioSchemas/bioschemas.github.io/master/_data/profile_versions.yaml"
    )
    content = response.text
    dict_content = yaml.safe_load(content)
    return dict_content


@DeprecationWarning
def parse_profile(jsonld, url_dl):
    """_summary_

    Args:
        jsonld (_type_): _description_
        url_dl (_type_): _description_

    Returns:
        _type_: _description_
    """

    profile_dict = {
        "name": "",
        "target_classes": [],
        "file": url_dl,
        "required": ["dct:conformsTo"],
        "recommended": [],
        "optional": [],
        "id": "",
        "ref_profile": "",
    }

    profiles_versions = request_profile_versions()

    for element in jsonld["@graph"]:
        if element["@type"] == "rdfs:Class":
            # print("Class: " + element["@id"])
            name = element["rdfs:label"]
            profile_dict["id"] = element["@id"].replace("bioschemas", "bsc")
            profile_dict["name"] = name

            sc_type = element["rdfs:subClassOf"]["@id"]

            # replace DDE prefix by schema.org prefix for Schema.org types
            replace_prefix = {
                "bioschemastypes:": "sc:",
                # "bioschemastypesdrafts:": "sc:",
                "schema:": "sc:",
            }
            for i, j in replace_prefix.items():
                sc_type = sc_type.replace(i, j)

            profile_dict["target_classes"].append(sc_type)
            if "schema:schemaVersion" in element.keys():
                profile_dict["ref_profile"] = element["schema:schemaVersion"][0]
            else:
                if profiles_versions[name]["latest_release"]:
                    latest_version = profiles_versions[name]["latest_release"]
                else:
                    latest_version = profiles_versions[name]["latest_publication"]

                bs_profile_url_base = "https://bioschemas.org/profiles/" + name + "/"
                bs_profile_url_path = bs_profile_url_base + latest_version
                # bs_profile_url_path = bs_profile_url_base + url_dl.split("/")[-1].replace("_v", "/").strip(".json")
                profile_dict["ref_profile"] = bs_profile_url_path
                # r = requests.head(bs_profile_url_path, verify=False, timeout=5) # it is faster to only request the header
                # print(r.status_code)
            break
        # if element["@type"] == "rdf:Property":
        #     additional_properties.append(element["@id"].replace("bioschemas", "bsc"))

    importance_levels = ["required", "recommended", "optional"]

    for importance in importance_levels:
        if importance in jsonld["@graph"][0]["$validation"]:
            for property in jsonld["@graph"][0]["$validation"][importance]:

                added = False
                # Identifying non Schema properties
                for element in jsonld["@graph"]:
                    if (
                        element["@type"] == "rdf:Property"
                        and property == element["rdfs:label"]
                    ):
                        profile_dict[importance].append(
                            element["@id"].replace("bioschemas", "bsc")
                        )
                        added = True
                if added:
                    continue
                profile_dict[importance].append("sc:" + property)

    # for compatibility with existing code
    profile_dict["min_props"] = profile_dict.pop("required")
    profile_dict["rec_props"] = profile_dict.pop("recommended")

    return profile_dict


def load_profiles():
    if not path.exists("profiles/bs_profiles.json"):
        print("Updating Bioschemas profiles from github")
        profiles = get_profiles_from_dde()
        # profiles = get_profiles_specs_from_github()
        with open("profiles/bs_profiles.json", "w") as outfile:
            json.dump(profiles, outfile)
        print("Profiles updated")
    else:
        print("Reading Bioschemas profiles from local file")
        # Opening JSON file
        with open("profiles/bs_profiles.json", "r") as openfile:
            # Reading from json file
            profiles = json.load(openfile)
    return profiles


def update_profiles():
    if path.exists("profiles/bs_profiles.json"):
        os.remove("profiles/bs_profiles.json")
        load_profiles()


def find_conformsto_subkg(kg):
    kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
    kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
    kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

    query_conformsto = """
        PREFIX dct: <http://purl.org/dc/terms/>

        SELECT ?x ?profile ?type WHERE {
            GRAPH ?g {
                ?x dct:conformsTo ?profile .
                ?x rdf:type ?type .
            }
        }
    """

    sub_kg_list = []

    results = kg.query(query_conformsto)
    for r in results:
        conformsto = r["profile"].strip("/")
        identifier = r["x"]
        type = r["type"]
        sub_kg = ConjunctiveGraph()

        for s, p, o, g in kg.quads((identifier, None, None, None)):

            sub_kg.add((s, p, o, g))
        # print(sub_kg.serialize(format="json-ld"))
        print(sub_kg.serialize(format="trig"))
        # if self.get_ref_profile() == conformsto:
        print(f"Found instance of type {type} that should conforms to {conformsto}")
        sub_kg_list.append(
            {
                "sub_kg": sub_kg,
                "subject": identifier,
                "profile": conformsto,
                "type": type,
            }
        )

    return sub_kg_list


def dyn_evaluate_profile_with_conformsto(kg):
    """_summary_

    Args:
        kg (_type_): _description_

    Returns:
        _type_: _description_
    """
    results = {}

    # Evaluate only profile with conformsTo
    ct_sub_kg_list = find_conformsto_subkg(kg)
    print(ct_sub_kg_list)

    for ct_sub_kg in ct_sub_kg_list:
        s = ct_sub_kg["subject"]
        ct = ct_sub_kg["profile"]
        t = ct_sub_kg["type"]
        sub_kg = ct_sub_kg["sub_kg"]

        try:
            profile = ProfileFactory.create_profile_from_remote(ct)
            shacl_shape = profile.get_shacl_shape()
            # print(shacl_shape)
            conforms, warnings, errors = profile.validate_shape(sub_kg, shacl_shape)
            # we override the final result to exclude warnings
            conforms = len(errors) == 0
            results[str(s)] = {
                "method": "by_conformsto",
                "type": str(t),
                "ref_profile": profile.get_ref_profile(),
                "conforms": conforms,
                "warnings": warnings,
                "errors": errors,
                "deprecated": profile.get_is_deprecated(),
                "latest_profile": profile.get_latest_profile(),
            }
        except BioschemasProfileNotFoundException as e:
            print(e)
            profile_versions = request_profile_versions()
            profile_name = ct.split("/")[-2]
            bs_latest_profile = get_latest_ref_profile_from_pname(
                profile_name, profile_versions
            )
            print(bs_latest_profile)
            print("TOTO")
            profile = ProfileFactory.create_profile_from_ref_profile(bs_latest_profile)

            print(profile)

    return results


@DeprecationWarning
def evaluate_profile_with_conformsto(kg):
    # A instancier au lancement du serveur et actualiser lors d'updates

    list_all_ct = ProfileFactory.list_all_conformsto()

    results = {}

    # Evaluate only profile with conformsTo
    ct_sub_kg_list = find_conformsto_subkg(kg)

    for ct_sub_kg in ct_sub_kg_list:
        s = ct_sub_kg["subject"]
        ct = ct_sub_kg["profile"]
        t = ct_sub_kg["type"]
        sub_kg = ct_sub_kg["sub_kg"]

        if ct in list_all_ct:
            ct_profile = ProfileFactory.create_profile_from_ref_profile(ct)

            if ct_profile is not None:
                shacl_shape = ct_profile.get_shacl_shape()
                print(shacl_shape)
                conforms, warnings, errors = ct_profile.validate_shape(
                    sub_kg, shacl_shape
                )
                # we override the final result to exclude warnings
                conforms = len(errors) == 0

                results[str(s)] = {
                    "type": str(t),
                    "ref_profile": ct_profile.get_ref_profile(),
                    "conforms": conforms,
                    "warnings": warnings,
                    "errors": errors,
                }
    return results


def evaluate_profile_from_type(kg):
    # A instancier au lancement du serveur et actualiser lors d'updates

    results = {}

    # Try to match and evaluate all found corresponding profiles
    for p_key in PROFILES.keys():
        sub_kg_list = PROFILES[p_key].match_sub_kgs_from_profile(kg)

        if sub_kg_list:
            for sub_kg in sub_kg_list:
                s = sub_kg["subject"]
                if not str(s) in results.keys():
                    o = sub_kg["object"]
                    sub_kg = sub_kg["sub_kg"]
                    shacl_shape = PROFILES[p_key].get_shacl_shape()
                    conforms, warnings, errors = PROFILES[p_key].validate_shape(
                        sub_kg, shacl_shape
                    )

                    # we override the final result to exclude warnings
                    conforms = len(errors) == 0
                    results[str(s)] = {
                        "method": "by_type",
                        "type": str(o),
                        "ref_profile": PROFILES[p_key].get_ref_profile(),
                        "conforms": conforms,
                        "warnings": warnings,
                        "errors": errors,
                        "deprecated": PROFILES[p_key].get_is_deprecated(),
                        "latest_profile": PROFILES[p_key].get_latest_profile(),
                    }
    return results


def is_profile_deprecated(profile_name, profile_versions):
    # profile_versions = request_profile_versions()
    if profile_name in profile_versions.keys():
        if profile_versions[profile_name]["status"] == "deprecated":
            return True
        elif profile_versions[profile_name]["status"] == "active":
            return False
        else:
            return False


def is_profile_version_latest(profile_name, version, profile_versions):

    # profile_versions = request_profile_versions()

    if profile_name in profile_versions.keys():
        if profile_versions[profile_name]["latest_release"] == version:
            return True
        elif profile_versions[profile_name]["latest_publication"] == version:
            return True
        else:
            return False
    else:
        return False


def get_latest_ref_profile_from_pname(profile_name, profile_versions):

    bs_ref_profile_base = "https://bioschemas.org/profiles/" + profile_name + "/"

    # profile_versions = request_profile_versions()
    if profile_name in profile_versions.keys():
        if profile_versions[profile_name]["latest_release"]:
            latest_profile_version = profile_versions[profile_name]["latest_release"]
            bs_ref_profile_latest = bs_ref_profile_base + latest_profile_version
            if requests.head(bs_ref_profile_latest, verify=False).status_code == 200:
                return bs_ref_profile_latest
            else:
                return None
        elif profile_versions[profile_name]["latest_publication"]:
            latest_profile_version = profile_versions[profile_name][
                "latest_publication"
            ]
            bs_ref_profile_latest = bs_ref_profile_base + latest_profile_version
            if requests.head(bs_ref_profile_latest, verify=False).status_code == 200:
                return bs_ref_profile_latest
            else:
                return None
        else:
            return None
    else:
        return None


# from enum import Enum, unique

# @unique
# class Implem(Enum):
#     FAIR_CHECKER = 1
#     FAIR_METRICS_API = 2


class ProfileFactory:
    @staticmethod
    def list_all_conformsto():
        bs_profiles = load_profiles()
        list_ct = [bs_profiles[p_key]["ref_profile"] for p_key in bs_profiles.keys()]

        return list_ct

    @staticmethod
    def create_profile_from_remote(bioschemas_profile_url):
        """generates a compact representation of a profile

        Args:
            bioschemas_profile_url (str): from the profile URL,
            generates the JSON file GitHub URL, parse it and
            returns its compact representation.

        Returns:
            dict: compact representation of the profile
        """
        p = bioschemas_profile_url
        version = p.split("/")[-1]
        profile_name = p.split("/")[-2]
        print(f"Profile {profile_name} version {version}")
        github_file = f"https://raw.githubusercontent.com/BioSchemas/specifications/master/{profile_name}/jsonld/{profile_name}_v{version}.json"
        response_header = requests.head(github_file)
        if response_header.status_code != 200:
            raise BioschemasProfileNotFoundException(
                f"Cannot access file <{github_file}> for profile <{profile_name}> version <{version}> at <{p}>"
            )
        # response = requests.get(github_file)
        # dict_profile = parse_profile(response.json(), github_file)

        dict_profile = profile_file_parser(github_file)
        dict_profile = dict_profile[bioschemas_profile_url]

        # get latest profile versions
        profile_versions = request_profile_versions()

        # Check if the profile in dct:conformsTo is deprecated
        is_deprecated = is_profile_deprecated(profile_name, profile_versions)

        # Check if the profile in dct:conformsTo is the latest one
        is_latest_profile = is_profile_version_latest(
            profile_name, version, profile_versions
        )
        if is_latest_profile:
            latest_ref_profile = True
        else:
            latest_ref_profile = get_latest_ref_profile_from_pname(
                profile_name, profile_versions
            )

        print("#####################")
        print("Deprecated: " + str(is_deprecated))
        print("Latest: " + str(latest_ref_profile))
        print("#####################")

        profile = Profile(
            shape_name=dict_profile["name"],
            target_classes=dict_profile["target_classes"],
            min_props=dict_profile["required"],
            rec_props=dict_profile["recommended"],
            ref_profile=dict_profile["ref_profile"],
            deprecated=is_deprecated,
            latest=latest_ref_profile,
        )
        return profile

    @staticmethod
    def create_profile_from_ref_profile(ref_profile):
        bs_profiles = load_profiles()
        for profile_key in bs_profiles.keys():
            print(bs_profiles[profile_key]["ref_profile"])
            if ref_profile == bs_profiles[profile_key]["ref_profile"]:
                name = bs_profiles[profile_key]["name"]
                profile = Profile(
                    shape_name=name,
                    target_classes=bs_profiles[profile_key]["target_classes"],
                    min_props=bs_profiles[profile_key]["required"],
                    rec_props=bs_profiles[profile_key]["recommended"],
                    ref_profile=bs_profiles[profile_key]["ref_profile"],
                )
                return profile

    @staticmethod
    def create_all_profiles_from_specifications():
        profiles = {}
        bs_profiles = load_profiles()
        for profile_key in bs_profiles.keys():
            profiles[profile_key] = Profile(
                shape_name=bs_profiles[profile_key]["name"],
                target_classes=bs_profiles[profile_key]["target_classes"],
                min_props=bs_profiles[profile_key]["required"],
                rec_props=bs_profiles[profile_key]["recommended"],
                ref_profile=bs_profiles[profile_key]["ref_profile"],
            )
        return profiles


PROFILES = ProfileFactory.create_all_profiles_from_specifications()
