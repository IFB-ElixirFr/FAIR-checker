# Représentation de FAIRChecker_V2
# Nouvelle version

# Auteur....................... : Philippe Lamarre
# date de création............. : 22 mai 2024
# date de dernière modification : mercredi 12 juin

from TSoR import *

from Measures.FAIRPrinciples import FAIR
from sympy import Symbol


# =======================================================================================
# =======================================================================================
#                                Measure FAIRChecker_V2
# =======================================================================================
# =======================================================================================

# Convention de nommage : les noms des nœuds (et des variables) commencent par FC_
# ----------------------
# Structure d'analyse
# ----------------------
FAIRChecker_V2 = FAIR.duplicate(
    name="FAIRChecker_V2",
    Description="""FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.

Data providers and consumers can check how FAIR are web resources. Developers can explore and inspect metadata exposed in web resources.""",
    URL="https://fair-checker.france-bioinformatique.fr",
    Prefixes={
        "sd": "@prefix sd: <http://www.w3.org/ns/sparql-service-description#> .",
        "xsd": "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "rdf": "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "rdfs": "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "dct": "@prefix dct: <http://purl.org/dc/terms/> .",
        "doap": "@prefix doap: <http://usefulinc.com/ns/doap#> .",
        "earl": "@prefix earl: <http://www.w3.org/ns/earl#> .",
        "kgi": "@prefix kgi: <http://ns.inria.fr/kg/index#> .",
        "prov": "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "mf": "@prefix mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#> .",
        "dataid": "@prefix dataid: <http://dataid.dbpedia.org/ns/core#> .",
        "dcat": "@prefix dcat: <http://www.w3.org/ns/dcat#> .",
        "dce": "@prefix dce: <http://purl.org/dc/elements/1.1/> .",
        "dct": "@prefix dct: <http://purl.org/dc/terms/> .",
        "dqv": "@prefix dqv: <http://www.w3.org/ns/dqv#> .",
        "foaf": "@prefix foaf: <http://xmlns.com/foaf/0.1/> .",
        "pav": "@prefix pav: <http://purl.org/pav/> .",
        "schema": "@prefix schema: <http://schema.org/> .",
        "void": "@prefix void: <http://rdfs.org/ns/void#> .",
        "odrl": "@prefix odrl: <http://www.w3.org/ns/odrl/2/>",
    },
    EquivalentPropertiesMeasure=[],
    WeightPrinciple="equivalentRequirements",
)


# ----------------------
# Requirements
# ----------------------

# description des requirements et ajout dans le dictionnaire
FC_R_F1A = Requirement(
    "FC_R_F1A",
    Description="""FAIRChecker checks that the resource identifier is a reachable URL. It's better if the URL is persistent (WebID, PURL or DOI).""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_F1B = Requirement(
    "FC_R_F1B",
    Description="""Weak : FAIR-Checker verifies that at least one namespace from identifiers.org is used in metadata.

Strong : FAIR-Checker verifies that the “identifier” property from DCTerms or Schema.org vocabularies is present in metadata.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_F2A = Requirement(
    "FC_R_F2A",
    Description="""For weak assessment, FAIR-Checker verifies that at least one RDF triple can be found in metadata. For strong assessment, it searches for at least one property in dct:title dct:description dct:accessURL dct:downloadURL dcat:endpointURL dcat:endpointDescription.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_F2B = Requirement(
    "FC_R_F2B",
    Description="""Description:
Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)

Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)


FC_R_A1_1 = Requirement(
    "FC_R_A1.1",
    Description="""FAIR-Checker verifies that the resource is accessible via an open protocol, for instance the protocol needs to be HTTP.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_A1_2 = Requirement(
    "FC_R_A1.2",
    Description="""The protocol allows for an authentication and authorisation procedure where necessary.
FAIR-Checker verifies if access rights are specified in metadata through terms odrl:hasPolicy, dct:rights, dct:accessRights, or dct:license.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)


FC_R_I1 = Requirement(
    "FC_R_I1",
    Description="""FAIR-Checker verifies that at least one RDF triple can be found in metadata.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_I2 = Requirement(
    "FC_R_I2",
    Description="""Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)

Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_I3 = Requirement(
    "FC_R_I3",
    Description="""FAIR-Checker verifies that at least 3 different URL authorities are used in the URLs of RDF metadata.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)


FC_R_R1_1 = Requirement(
    "FC_R_R1.1",
    Description="""Metadata includes license.
FAIR-Checker verifies that at least one license property from Schema.org, DCTerms, or DOAP ontologies are found in metadata.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_R1_2 = Requirement(
    "FC_R_R1.2",
    Description="""Metadata includes provenance.
FAIR-Checker verifies that at least one provenance property from PROV, DCTerms, or PAV ontologies are found in metadata.""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)
FC_R_R1_3 = Requirement(
    "FC_R_R1.3",
    Description="""Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)

Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)""",
    URL="https://fair-checker.france-bioinformatique.fr/check",
)


# positionnement dans l'arbre

FAIRChecker_V2["Findable"]["F1"].requires(FC_R_F1A)
FAIRChecker_V2["Findable"]["F1"].requires(FC_R_F1B)
FAIRChecker_V2["Findable"]["F2"].requires(FC_R_F2A)
FAIRChecker_V2["Findable"]["F2"].requires(FC_R_F2B)

FAIRChecker_V2["Accessible"]["A1"]["A1.1"].requires(FC_R_A1_1)
FAIRChecker_V2["Accessible"]["A1"]["A1.2"].requires(FC_R_A1_2)

FAIRChecker_V2["Interoperable"]["I1"].requires(FC_R_I1)
FAIRChecker_V2["Interoperable"]["I2"].requires(FC_R_I2)
FAIRChecker_V2["Interoperable"]["I3"].requires(FC_R_I3)

FAIRChecker_V2["Reusable"]["R1"]["R1.1"].requires(FC_R_R1_1)
FAIRChecker_V2["Reusable"]["R1"]["R1.2"].requires(FC_R_R1_2)
FAIRChecker_V2["Reusable"]["R1"]["R1.3"].requires(FC_R_R1_3)


# ----------------------
# Implémentations
# ----------------------
# Implémentations de FAIRChecker_V2 :
# --------------------------------------
FC_I_F1A = Implementation(
    "FC_I_F1A",
    Version=None,  # not found in the code
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/F1A_Impl.py",
    MinimalPatternsForSuccess={
        0: [
            [
                "# FC_I_F1A > Status code is different than 200, thus, the resource is not reachable."
            ]
        ],
        1: [[]],
        2: [["# FC_I_F1A > Status code is OK, meaning the url is Unique."]],
    },
    ScoreMin=0,  # to be set
    ScoreMax=2,  # to be set
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)


FC_I_F1B = Implementation(
    "FC_I_F1B",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/F1B_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [
            [
                "# FC_I_F1B > at least one namespace from identifiers.org is used in metadata"
            ]
        ],
        2: [["# FC_I_F1B > ", "?sIdentifier dct:identifier ?oIdentifier ."]],
    },
    EquivalentPropertiesImplem=[{"dct:identifier", "schema:identifier"}],
    ScoreMin=0,  # to be set
    ScoreMax=2,  # to be set
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_F2A = Implementation(
    "FC_I_F2A",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/F2A_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [["# FC_I_F2A > one triple in metadata"]],
        2: [["# FC_I_F2A > ", "?sTitle dct:title ?oTitle ."]],
    },
    EquivalentPropertiesImplem=[
        {
            "dct:title",
            "dct:description",
            "dcat:accessURL",
            "dcat:downloadURL",
            "dcat:endpointDescription",
            "dcat:endpointURL",
        }
    ],
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_F2B = Implementation(
    "FC_I_F2B",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/F2B_Impl.py",
    MinimalPatternsForSuccess={
        0: [
            [
                "# FC_I_F2B > No classes and properties are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
        1: [
            [
                "# FC_I_F2B > at least one used ontology classe or property known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
        2: [
            [
                "# FC_I_F2B > All classes and properties are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_A1_1 = Implementation(
    "FC_I_A1.1",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/A11_Impl.py",
    MinimalPatternsForSuccess={
        0: [
            [
                "# FC_I_A1.1 > The resource seems to not be using HTTP protocol, or can't be found: 404 error"
            ]
        ],
        1: [[]],
        2: [["# FC_I_A1.1 > The resource uses HTTP protocol"]],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_A1_2 = Implementation(
    "FC_I_A1.2",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/A12_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [[]],
        2: [["# FC_I_A1.2 > ", "?sLicense dct:license ?oLicense ."]],
    },
    EquivalentPropertiesImplem=[
        {
            "odrl:hasPolicy",
            "dct:rights",
            "dct:accessRights",
            "dct:license",
            "schema:license",
        }
    ],
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)


FC_I_I1 = Implementation(
    "FC_I_I1",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/I1A_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [["# FC_I_F2A > one triple in metadata"]],
        2: [["# FC_I_F2A > ", "?sTitle dct:title ?oTitle ."]],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)


FC_I_I2 = Implementation(
    "FC_I_I2",
    Version="",
    URL="",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [
            [
                "# FC_I_I2 > at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
        2: [
            [
                "# FC_I_I2 > all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)

FC_I_I3 = Implementation(
    "FC_I_I3",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/I3_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [[]],
        2: [
            [
                "# FC_I_I3 > At least 3 different domains were found in metadata",
                """<http://www.wikidata.org/entity/Q12418> dct:title "La Joconde" .""",
                """<http://data.europeana.eu/item/04802/243FA8618938F4117025F17A8B813C5F9AA4D619> dct:subject <http://www.wikidata.org/entity/Q12418> .""",
                """<http://www.qsdfmlknqf.com/AZT489> dct:title "For example" .""",
            ]
        ],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_R1_1 = Implementation(
    "FC_I_R1.1",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/R11_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [[]],
        2: [["# FC_I_R1.1 > ", "?sLicense dct:license ?oLicense ."]],
    },
    EquivalentPropertiesImplem=[
        {
            "schema:license",
            "dct:license",
            "doap:license",
            "dbpedia-owl:license",
            "cc:license",
            "xhv:license",
            "sto:license",
            "nie:license",
        }
    ],
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)
FC_I_R1_2 = Implementation(
    "FC_I_R1.2",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/R12_Impl.py",
    MinimalPatternsForSuccess={
        0: [[]],
        1: [[]],
        2: [["# FC_I_R1.2", "?sCreator dct:creator ?oCreator ."]],
    },
    EquivalentPropertiesImplem=[
        {
            "prov:wasGeneratedBy",
            "prov:wasDerivedFrom",
            "prov:wasAttributedTo",
            "prov:used",
            "prov:wasInformedBy",
            "prov:wasAssociatedWith",
            "prov:startedAtTime",
            "prov:endedAtTime",
            "dct:hasVersion",
            "dct:isVersionOf",
            "dct:creator",
            "dct:contributor",
            "dct:publisher",
            "pav:hasVersion",
            "pav:version",
            "pav:hasCurrentVersion",
            "pav:createdBy",
            "pav:authoredBy",
            "pav:retrievedFrom",
            "pav:importedFrom",
            "pav:createdWith",
            "pav:retrievedBy",
            "pav:importedBy",
            "pav:curatedBy",
            "pav:createdAt",
            "pav:previousVersion",
            "schema:creator",
            "schema:author",
            "schema:publisher",
            "schema:provider",
            "schema:funder",
        }
    ],
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=2,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)


FC_I_R1_3 = Implementation(
    "FC_I_R1.3",
    Version="",
    URL="https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/R13_Impl.py",
    MinimalPatternsForSuccess={
        0: [
            [
                "# FC_I_F2B > No classes and properties are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
        1: [
            [
                "# FC_I_R1.3 > at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
        2: [
            [
                "# FC_I_R1.3 > all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)"
            ]
        ],
    },
    ScoreMin=0,
    ScoreMax=2,
    ScoreIntervalNature="Discrete",
    NbPossibleScores=3,
    observedProbabilityOfSuccess=None,  # Probabilité de succès observée pour cette immplentation
    probabilityOfSuccess=None,  # Probabilité de succès utilisée pour les random pour cette immplentation
)


# Dépendances entre les implémentations


s = Symbol("s")
# Possibilité d'exprimer des expression du genre
# implementationDependance(("FC_I_F2A", s), ("FC_I_I1", (s+2) * 3))
# Possibilité d'exprimer des contraintes par points :
# implementationDependance(("FC_I_F2A", 1), ("FC_I_I1", 2))
# Possibilité d'exprimer des contraintes qui portent sur des intervalles
# implementationDependance(("FC_I_F2A", 1), ("FC_I_I1", [1, 2]))


# Les deux implémentations : FC_I_F1A et FC_I_I1 sont strictement équivalentes
# en effet, FC_I_I1 élègue l'évaluation à FC_I_F1A
implementationDependance(("FC_I_F2A", s), ("FC_I_I1", s))
implementationDependance(("FC_I_I1", s), ("FC_I_F2A", s))


# Les trois implémentations suivantes sont équivalentes : FC_R_F2B, PC_I_I2 et FC_I_R1.3
# En effet, les deux dernières déléguent l'évaluation à la première
implementationDependance(("FC_I_F2B", s), ("FC_I_I2", s))
implementationDependance(("FC_I_F2B", s), ("FC_I_R1.3", s))

implementationDependance(("FC_I_I2", s), ("FC_I_F2B", s))
implementationDependance(("FC_I_I2", s), ("FC_I_R1.3", s))

implementationDependance(("FC_I_R1.3", s), ("FC_I_F2B", s))
implementationDependance(("FC_I_R1.3", s), ("FC_I_I2", s))


# positionnement des implémentations dans l'arbre


FAIRChecker_V2["Findable"]["F1"]["FC_R_F1A"].isImplementedBy(FC_I_F1A)
FAIRChecker_V2["Findable"]["F1"]["FC_R_F1B"].isImplementedBy(FC_I_F1B)
FAIRChecker_V2["Findable"]["F2"]["FC_R_F2A"].isImplementedBy(FC_I_F2A)
FAIRChecker_V2["Findable"]["F2"]["FC_R_F2B"].isImplementedBy(FC_I_F2B)
FAIRChecker_V2["Accessible"]["A1"]["A1.1"]["FC_R_A1.1"].isImplementedBy(FC_I_A1_1)
FAIRChecker_V2["Accessible"]["A1"]["A1.2"]["FC_R_A1.2"].isImplementedBy(FC_I_A1_2)
FAIRChecker_V2["Interoperable"]["I1"]["FC_R_I1"].isImplementedBy(FC_I_I1)  # Délégation
FAIRChecker_V2["Interoperable"]["I2"]["FC_R_I2"].isImplementedBy(FC_I_I2)  # Délégation
FAIRChecker_V2["Interoperable"]["I3"]["FC_R_I3"].isImplementedBy(FC_I_I3)
FAIRChecker_V2["Reusable"]["R1"]["R1.1"]["FC_R_R1.1"].isImplementedBy(FC_I_R1_1)
FAIRChecker_V2["Reusable"]["R1"]["R1.2"]["FC_R_R1.2"].isImplementedBy(FC_I_R1_2)
FAIRChecker_V2["Reusable"]["R1"]["R1.3"]["FC_R_R1.3"].isImplementedBy(
    FC_I_R1_3
)  # Délégation
