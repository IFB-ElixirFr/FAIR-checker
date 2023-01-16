from profiles.Profile import Profile
from os import environ, path
import requests
import re
import json

# from profiles.bioschemas_shape_gen import bs_profiles


def gen_shacl_alternatives(bs_profiles):
    res = {}
    for p in bs_profiles.keys():
        res[p] = {}
        min = []
        rec = []
        for prop in bs_profiles[p]["min_props"]:
            if "|" in prop:
                shacl_alt = f'[ sh:alternativePath (  {" ".join(prop.split("|"))} ) ]'
                min.append(shacl_alt)
            else:
                min.append(prop)

        for prop in bs_profiles[p]["rec_props"]:
            if "|" in prop:
                shacl_alt = f'[ sh:alternativePath (  {" ".join(prop.split("|"))} ) ]'
                rec.append(shacl_alt)
            else:
                rec.append(prop)

        res[p]["rec_props"] = rec
        res[p]["min_props"] = min
        res[p]["ref_profile"] = bs_profiles[p]["ref_profile"]
    return res


bs_profiles = {
    "sc:SoftwareApplication": {
        "min_props": ["sc:name", "sc:description", "sc:url"],
        "rec_props": [
            "sc:additionalType",
            "sc:applicationCategory",
            "sc:applicationSubCategory",
            "sc:author",
            "sc:license",
            "sc:citation",
            "sc:featureList",
            "sc:softwareVersion",
        ],
        "ref_profile": "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE",
    },
    "sc:Dataset": {
        "min_props": [
            "sc:name",
            "sc:description",
            "sc:identifier",
            "sc:keywords",
            "sc:license",
            "sc:url",
        ],
        "rec_props": [
            "sc:alternateName",
            "sc:creator",
            "sc:citation",
            "sc:distribution",
            "sc:includedInDataCatalog",
            "sc:isBasedOn",
            "sc:measurementTechnique",
            "sc:variableMeasured",
            "sc:version",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Dataset/0.4-DRAFT",
    },
    "sc:ScholarlyArticle": {
        "min_props": ["sc:headline", "sc:identifier"],
        "rec_props": [
            "sc:about",
            "sc:alternateName",
            "sc:author",
            "sc:backstory",
            "sc:citation",
            "sc:dateCreated",
            "sc:dateModified",
            "sc:datePublished",
            "sc:isBasedOn",
            "sc:isPartOf",
            "sc:keywords",
            "sc:license",
            "sc:pageEnd",
            "sc:pageStart",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/ScholarlyArticle/0.2-DRAFT-2020_12_03",
    },
    "sc:MolecularEntity": {
        "min_props": ["sc:identifier", "sc:name", "dct:conformsTo", "sc:url"],
        "rec_props": [
            "sc:inChI",
            "sc:inChIKey",
            "sc:iupacName",
            "sc:molecularFormula",
            "sc:molecularWeight",
            "sc:smiles",
        ],
        "ref_profile": "https://bioschemas.org/profiles/MolecularEntity/0.5-RELEASE",
    },
    "sc:Gene": {
        "min_props": ["sc:identifier", "sc:name", "dct:conformsTo"],
        "rec_props": [
            "sc:description",
            "sc:encodesBioChemEntity",
            "sc:isPartOfBioChemEntity",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Gene/1.0-RELEASE",
    },
    "bsc:Gene": {
        "min_props": ["sc:identifier", "sc:name", "dct:conformsTo"],
        "rec_props": [
            "sc:description",
            "sc:encodesBioChemEntity",
            "sc:isPartOfBioChemEntity",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Gene/1.0-RELEASE",
    },
    "sc:Study": {
        "min_props": [
            "sc:identifier",
            "sc:name",
            "dct:conformsTo",
            "sc:author",
            "sc:datePublished",
            "sc:description",
            "bsc:studyDomain",
            "sc:studySubject",
        ],
        "rec_props": [
            "sc:about",
            "sc:additionnalProperty",
            "sc:citation",
            "sc:creator",
            "sc:dateCreated",
            "sc:endDate",
            "sc:keywords",
            "sc:startDate",
            "sc:studyLocation",
            "bsc:studyProcess",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Study/0.2-DRAFT",
    },
    "sc:Person": {
        "min_props": [
            "sc:description",
            "sc:name",
            "dct:conformsTo",
            "sc:mainEntityOfPage",
        ],
        "rec_props": [
            "sc:email",
            "bsc:expertise",
            "sc:homeLocation",
            "sc:image",
            "sc:memberOf",
            "bsc:orcid",
            "sc:worksFor",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Person/0.2-DRAFT-2019_07_19",
    },
    "sc:SoftwareSourceCode": {
        "min_props": [
            "dct:conformsTo",
            "sc:creator",
            "sc:dateCreated",
            "bsc:input|sc:input",
            "sc:license",
            "sc:name",
            "bsc:output|sc:output",
            "sc:programmingLanguage",
            "sc:sdPublisher",
            "sc:url",
            "sc:version",
        ],
        "rec_props": [
            "sc:citation",
            "sc:contributor",
            "sc:creativeWorkStatus",
            "sc:description",
            "sc:documentation",
            "sc:funding",
            "sc:hasPart",
            "sc:isBasedOn",
            "sc:keywords",
            "sc:maintainer",
            "sc:producer",
            "sc:publisher",
            "sc:runtimePlatform",
            "sc:sofwtareRequirement",
            "sc:targetProduct",
        ],
        "ref_profile": "https://bioschemas.org/profiles/ComputationalWorkflow/1.0-RELEASE",
    },
    "sc:Protein": {
        "min_props": ["dct:conformsTo", "sc:identifier", "sc:name"],
        "rec_props": [
            "bsc:associatedDisease",
            "sc:description",
            "bsc:isEncodedByBioChemEntity",
            "bsc:taxonomicRange",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/Protein/0.11-RELEASE",
    },
    "sc:SequenceAnnotation": {
        "min_props": ["dct:conformsTo", "bsc:sequenceLocation|sc:sequenceLocation"],
        "rec_props": [
            "bsc:creationMethod",
            "sc:description",
            "sc:image",
            "sc:name",
            "sc:sameAs",
            "bsc:sequenceOrientation",
            "bsc:sequenceValue",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/SequenceAnnotation/0.7-DRAFT",
    },
    "sc:SequenceRange": {
        "min_props": ["dct:conformsTo", "bsc:rangeStart", "bsc:rangeEnd"],
        "rec_props": ["bsc:endUncertainty", "bsc:startUncertainty"],
        "ref_profile": "https://bioschemas.org/profiles/SequenceRange/0.1-DRAFT",
    },
    "sc:CreativeWork": {
        "min_props": ["dct:conformsTo", "sc:description", "sc:keywords", "sc:name"],
        "rec_props": [
            "sc:about",
            "sc:abstract",
            "sc:audience",
            "sc:author",
            "sc:competencyRequired",
            "sc:educationalLevel",
            "sc:identifier",
            "sc:inLanguage",
            "sc:learningResourceType",
            "sc:license",
            "sc:mentions",
            "sc:teaches",
            "sc:timeRequired",
            "sc:url",
        ],
        "ref_profile": "https://bioschemas.org/profiles/TrainingMaterial/0.9-DRAFT-2020_12_08",
    },
}

bs_profiles = gen_shacl_alternatives(bs_profiles)


def get_profiles_specs_from_github(self):
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
                                and not "DEPRECATED" in file["download_url"]
                            ):
                                regex_version = "_v([0-9]*.[0-9]*)-"
                                m = re.search(regex_version, file["download_url"])

                                if "RELEASE" in file["download_url"]:
                                    releases[file["download_url"]] = float(m.group(1))
                                    # releases[m.group(1)] = res["download_url"]
                                elif "DRAFT" in file["download_url"]:
                                    drafts[file["download_url"]] = float(m.group(1))

                        latest_url_dl = ""
                        if releases:
                            latest_url_dl = self.get_latest_profile(releases)

                        elif drafts:
                            latest_url_dl = self.get_latest_profile(drafts)

                        if latest_url_dl:
                            response = requests.get(latest_url_dl, headers=headers)
                            jsonld = response.json()
                            profile_dict = self.parse_profile(
                                jsonld, profile_name, latest_url_dl
                            )

                            profiles_dict["sc:" + profile_dict["name"]] = profile_dict
        return profiles_dict
    else:
        return False

def get_latest_profile(self, profiles_dict):

    latest_rel = max(profiles_dict.values())

    # latest_url_dl = list(profiles_dict.keys())[list(profiles_dict.values()).index(latest_rel)]
    latest_url_dl = [k for k, v in profiles_dict.items() if v == latest_rel]
    return latest_url_dl[0]

def parse_profile(self, jsonld, url_dl):
    profile_dict = {
        "name": "",
        "file": url_dl,
        "required": ["dct:conformsTo"],
        "recommended": [],
        "optional": [],
        "id": "",
        "ref_profile": "",
    }

    additional_properties = []
    for element in jsonld["@graph"]:
        if element["@type"] == "rdfs:Class":
            # print("Class: " + element["@id"])
            profile_dict["id"] = element["@id"].replace("bioschemas", "bsc")
            profile_dict["name"] = element["rdfs:label"]
            if "schema:schemaVersion" in element.keys():
                profile_dict["ref_profile"] = element["schema:schemaVersion"][0]
            else:
                bs_profile_url_base = "https://bioschemas.org/profiles/"
                bs_profile_url_path = bs_profile_url_base + url_dl.split("/")[-1].replace("_v", "/").strip(".json")
                profile_dict["ref_profile"] = bs_profile_url_path
                # print(bs_profile_url_path)
                r = requests.head(bs_profile_url_path,verify=False,timeout=5) # it is faster to only request the header
                # print(r.status_code)
            break
        # if element["@type"] == "rdf:Property":
        #     additional_properties.append(element["@id"].replace("bioschemas", "bsc"))

    importance_levels = [
        "required",
        "recommended",
        "optional"
    ]

    for importance in importance_levels:
        if importance in jsonld["@graph"][0]["$validation"]:
            for property in jsonld["@graph"][0]["$validation"][importance]:

                added = False
                # Identifying non Schema properties
                for element in jsonld["@graph"]:
                    if element["@type"] == "rdf:Property" and property == element["rdfs:label"]:
                        profile_dict[importance].append(element["@id"].replace("bioschemas", "bsc"))
                        added = True
                if added:
                    continue
                profile_dict[importance].append("sc:" + property)
    
    # for compatibility with existring code
    profile_dict["min_props"] = profile_dict.pop("required")
    profile_dict["rec_props"] = profile_dict.pop("recommended")

    return profile_dict

def load_profiles():
    if not path.exists("profiles/bs_profiles.json"):
        print("Updating from github")
        profiles = get_profiles_specs_from_github()
        with open("profiles/bs_profiles.json", "w") as outfile:
            json.dump(profiles, outfile)
    else:
        print("Reading from local file")
        # Opening JSON file
        with open("profiles/bs_profiles.json", "r") as openfile:
            # Reading from json file
            profiles = json.load(openfile)
    return profiles

# from enum import Enum, unique

# @unique
# class Implem(Enum):
#     FAIR_CHECKER = 1
#     FAIR_METRICS_API = 2


class ProfileFactory:

    #     template_create = """
    # def create_{name}_
    #     """



    @staticmethod
    def create_all_profiles():
        profiles = {}
        for p in bs_profiles.keys():
            name = bs_profiles[p]["ref_profile"].split("profiles/")[1]
            name = name.replace("/", "-")
            min_props = bs_profiles[p]["min_props"]
            rec_props = bs_profiles[p]["rec_props"]
            profiles[name] = Profile(
                shape_name=name,
                target_classes=[p],
                min_props=min_props,
                rec_props=rec_props,
            )
        return profiles

    @staticmethod
    def create_all_profiles_from_specifications():
        profiles = {}
        bs_profiles = load_profiles()
        for profile_key in bs_profiles.keys():
            name = bs_profiles[profile_key]["name"]
            profiles[name] = Profile(
                shape_name=name,
                target_classes=["sc:" + bs_profiles[profile_key]["name"]],
                min_props=bs_profiles[profile_key]["min_props"],
                rec_props=bs_profiles[profile_key]["rec_props"],
            )
        return profiles
