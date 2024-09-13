from pymongo import MongoClient
from rdflib import ConjunctiveGraph
from string import Template
import validators

FC_spec = [
    {"id": "F1A", "category": "Findable", "label": "Unique IDs", "definition": ""},
    {"id": "F1B", "category": "Findable", "label": "Persistent IDs", "definition": ""},
    {
        "id": "F2A",
        "category": "Findable",
        "label": "Structured metadata",
        "definition": "",
    },
    {
        "id": "F2B",
        "category": "Findable",
        "label": "Shared vocabularies for metadata",
        "definition": "",
    },
    {
        "id": "A11",
        "category": "Accessible",
        "label": "Open resolution protocol",
        "definition": "",
    },
    {
        "id": "A12",
        "category": "Accessible",
        "label": "Authorisation procedure or access rights",
        "definition": "",
    },
    {
        "id": "I1",
        "category": "Interoperable",
        "label": "Machine readable format",
        "definition": "",
    },
    {
        "id": "I2",
        "category": "Interoperable",
        "label": "Use shared ontologies",
        "definition": "",
    },
    {
        "id": "I3",
        "category": "Interoperable",
        "label": "External links",
        "definition": "",
    },
    {
        "id": "R11",
        "category": "Reusable",
        "label": "Metadata includes license",
        "definition": "",
    },
    {
        "id": "R12",
        "category": "Reusable",
        "label": "Metadata includes provenance",
        "definition": "",
    },
    {
        "id": "R13",
        "category": "Reusable",
        "label": "Community standards",
        "definition": "",
    },
]

prefix = """
@prefix daq: <http://purl.org/eis/vocab/daq#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix duv: <http://www.w3.org/ns/duv#> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

@prefix : <https://fair-checker.france-bioinformatique.fr/data#> .

"""

FAIR_Checker_template = """
:$metric_id
    a dqv:Dimension ;
    skos:prefLabel "$metric_label"@en ;
    skos:definition "$metric_definition"@en ;
    dqv:inCategory :$category ."""

metrics_tpl = """
:$id
    a dqv:QualityMeasurement ;
    dqv:computedOn <$url> ;
    dqv:isMeasurementOf :$dimension ;
    dqv:value "$value"^^xsd:integer ;
    prov:generatedAtTime "$date"^^xsd:dateTime ;
    prov:wasAttributedTo <https://github.com/IFB-ElixirFr/fair-checker> ;
    rdfs:seeAlso <https://doi.org/10.1186/s13326-023-00289-5> ."""

client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations

with open("fc_evaluations_dump.ttl", mode="w") as file_object:
    print(prefix, file=file_object)

    for spec in FC_spec:
        spec_ttl = Template(FAIR_Checker_template).safe_substitute(
            metric_id=spec["id"],
            metric_label=spec["label"],
            metric_definition=spec["definition"],
            category=spec["category"],
        )
        print(spec_ttl, file=file_object)

    i = 0
    for e in evaluations.find({}):
        d = None
        if e["ended_at"]:
            d = e["ended_at"].isoformat()
        if e["success"]:
            u = e["target_uri"].replace(" ", "").replace("\t", "")
            if validators.url(u):
                eval_ttl = Template(metrics_tpl).safe_substitute(
                    id=str(e["_id"]),
                    url=u,
                    dimension=e["metrics"],
                    value=e["success"],
                    date=d,
                )
            print(eval_ttl, file=file_object)
            i += 1
        if (i % 100000) == 0:
            print(f"Serialized {i} FAIR metrics evaluations")
            # break
