from flask import Flask, Response, request
from rdflib import ConjunctiveGraph
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

from metrics.Evaluation import Evaluation

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

@prefix : <https://fair-checker.france-bioinformatique.fr/data/> .
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

app = Flask(__name__)


client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations


@app.route("/data/<ID>")
def derefLD(ID):
    mimetype = None
    if "Content-Type" in request.headers:
        mimetype = request.headers["Content-Type"].split(";")[0]

    try:
        eval_json = evaluations.find_one({"_id": ObjectId(ID)})
        print(type(eval_json))
        print(eval_json)
        e = Evaluation()
        e.build_from_json(data=eval_json)
        ttl = e.to_rdf_turtle()
        kg = ConjunctiveGraph()
        try:
            kg.parse(data=ttl, format="turtle")
        except Exception:
            return Response(
                "Error while parsing RDF:\n\n" + e.to_rdf_turtle(), mimetype="text"
            )
        if mimetype == "application/json":
            return Response(kg.serialize(format="json-ld"), mimetype="application/json")
        elif mimetype == "application/ld+json":
            return Response(
                kg.serialize(format="json-ld"), mimetype="application/ld+json"
            )
        elif mimetype == "application/rdf+xml":
            return Response(kg.serialize(format="xml"), mimetype="application/rdf+xml")
        elif mimetype == "text/n3":
            return Response(kg.serialize(format="n3"), mimetype="text/n3")
        elif mimetype == "text/turtle":
            return Response(kg.serialize(format="turtle"), mimetype="text/turtle")
        else:
            return Response(kg.serialize(format="turtle"), mimetype="text/turtle")
    except InvalidId:
        return Response(f"Cannot find evaluation {ID}", mimetype="text")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
