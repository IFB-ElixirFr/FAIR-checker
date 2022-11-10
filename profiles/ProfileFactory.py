from profiles.Profile import Profile

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
