from typing import cast
from jinja2 import Template
from rdflib import Graph, RDF, BNode
from pyshacl import validate

import logging

logger = logging.getLogger(__name__)

### Mapping with  Schema.org
mandatory_schema_properties = [
    "organism part",
    "lifestage",
    "project name",
    "collected_by",
    "collection date",
    "geographic location (region and locality)",
    "habitat",
    "sex",
    "geographic location (country and/or sea)",
    "collecting institution",
]

recommended_schema_properties = [
    "geographic location (latitude)",
    "geographic location (longitude)",
    "specimen_voucher",
]

optional_schema_properties = [
    "Latitude Start",
    "Longitude Start",
    "Latitude End",
    "Longitude End",
    "relationship",
    "sample symbiont of",
    "symbiont",
    "sample collection method",
    "sample coordinator affiliation",
    "sample same as",
    "sample derived from",
    "barcoding center",
    "tolid",
    "identified_by",
    "elevation",
    "identifier_affiliation",
    "original collection date",
    "original geographic location",
    "original geographic location (latitude)",
    "original geographic location (longitude)",
    "sample coordinator",
    "GAL",
    "specimen_id",
    "GAL_sample_id",
    "proxy voucher",
    "proxy biomaterial",
    "bio_material",
    "culture_or_strain_id",
    "depth",
]

ena53_profile = {
    "target_class": ["http://schema.org/Sample"],
    "mandatory_properties": mandatory_schema_properties,
    "recommended_properties": recommended_schema_properties,
    "optional_properties": optional_schema_properties,
}

shape_tpl = """
    @prefix ns: <https://fair-checker.france-bioinformatique.fr#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix sc: <http://schema.org/> .
    @prefix scs: <https://schema.org/> .
    @prefix bsc: <https://bioschemas.org/> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix edam: <http://edamontology.org/> .
    @prefix biotools: <https://bio.tools/ontology/> .

    {% for target_class in target_classes %}
    ns:test_NG_shape_{{ loop.index }}
        a sh:NodeShape ;
        sh:targetClass <{{target_class}}> ;

        {% for min_prop in min_props %}
                sh:property [
                    sh:path sc:additionalProperty ;
                    sh:qualifiedValueShape [
                        sh:property [
                            sh:path sc:name ;
                            sh:hasValue "{{min_prop}}" ;
                        ] ;

                        sh:property [
                            sh:path sc:value ;
                            sh:not [
                                sh:in ( "missing" "None" ) ;
                            ] ;
                        ] ;
                    ] ;
                    sh:qualifiedMinCount 1 ;
                    sh:severity sh:Violation ;
                ] ;
        {% endfor %}

        {% for rec_prop in rec_props %}
                sh:property [
                    sh:path sc:additionalProperty ;
                    sh:qualifiedValueShape [
                        sh:property [
                            sh:path sc:name ;
                            sh:hasValue "{{rec_prop}}" ;
                        ] ;
                        sh:property [
                            sh:path sc:value ;
                            sh:not [
                                sh:in ( "missing" "None" ) ;
                            ] ;
                        ] ;
                    ] ;

                    sh:qualifiedMinCount 1 ;
                    sh:severity sh:Warning ;
                ] ;
        {% endfor %}
        
        {% for opt_prop in opt_props %}
                sh:property [
                    sh:path sc:additionalProperty ;
                    sh:qualifiedValueShape [
                        sh:property [
                            sh:path sc:name ;
                            sh:hasValue "{{opt_prop}}" ;
                        ] ;
                        sh:property [
                            sh:path sc:value ;
                            sh:not [
                                sh:in ( "missing" "None" ) ;
                            ] ;
                        ] ;
                    ] ;
                    sh:qualifiedMinCount 1 ;
                    sh:severity sh:Info
                ] ;
        {% endfor %}
    .
    {% endfor %}
"""

template = Template(shape_tpl)


def validate_shape(knowledge_graph, shacl_shape):
    r = cast(
        tuple[bool, Graph, str],
        validate(
            data_graph=knowledge_graph,
            data_graph_format="turtle",
            shacl_graph=shacl_shape,
            # shacl_graph = my_shacl_constraint,
            shacl_graph_format="turtle",
            ont_graph=None,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            debug=False,
        ),
    )

    conforms, results_graph, results_text = r

    report_query = """
            PREFIX sc: <http://schema.org/>
            SELECT ?node ?path ?severity ?prop_name WHERE {
                ?v rdf:type sh:ValidationReport ;
                   sh:result ?r .
                ?r sh:focusNode ?node ;
                   sh:sourceShape ?s .
                { ?s sh:path ?path ;
                   sh:severity ?severity . }
                UNION { ?s sh:path/sh:alternativePath/rdf:rest*/rdf:first ?path ;
                   sh:severity ?severity . }
                OPTIONAL {
                    ?s sh:qualifiedValueShape ?qvs .
                    ?qvs sh:property ?qprop .
                    ?qprop sh:path sc:name ;
                           sh:hasValue ?prop_name .
                }
                FILTER (! isBlank(?path))
            }
        """

    results = results_graph.query(report_query)
    warnings = []
    errors = []
    infos = []
    for r in results:
        label = str(r["prop_name"]) if r["prop_name"] else str(r["path"])  # type: ignore
        if "#Warning" in r["severity"]:  # type: ignore
            warnings.append(label)
        if "#Violation" in r["severity"]:  # type: ignore
            errors.append(label)
        if "#Info" in r["severity"]:  # type: ignore
            infos.append(label)

    return conforms, infos, warnings, errors


def validate_md(graph, profile):
    """
    Validates the given knowledge graph against the provided profile.
    """

    ## ensure that the profile includes "target_class", "mandatory_properties", "recommended_properties" and "optional_properties" keys
    required_keys = [
        "target_class",
        "mandatory_properties",
        "recommended_properties",
        "optional_properties",
    ]
    for key in required_keys:
        if key not in profile:
            logger.error(f"Profile is missing the required key: {key}")
            return

    shape = template.render(
        target_classes=profile["target_class"],
        min_props=profile["mandatory_properties"],
        rec_props=profile["recommended_properties"],
        opt_props=profile["optional_properties"],
    )

    try:
        shape_kg = Graph()
        shape_kg.parse(data=shape, format="turtle")
        assert len(shape_kg) > 0
        # print(f"Shape graph size: {len(shape_kg)} triples")
        # print(shape_kg.serialize(format="turtle"))
    except Exception as e:
        print("Error parsing the SHACL shape:", e)
        print("Shape content was:")
        print(shape)
        return

    results = {}

    print()
    for s, p, o in graph.triples((None, RDF.type, None)):

        # print(f"{s.n3(graph.namespace_manager)} is a {o.n3(graph.namespace_manager)}")
        # print(f"Profile target classes: {profile['target_class']}")
        # print(str(o))

        # if o.n3(graph.namespace_manager) in profile["target_class"]:
        logger.info(
            f"Checking if {str(o)} is in profile target classes: {profile['target_class']}"
        )
        logger.info(str(o) in profile["target_class"])

        if str(o) in profile["target_class"]:
            logger.info(f"{s} is a {o} and will be validated against the profile")

            sub_kg = Graph()
            for x, y, z in graph.triples((s, None, None)):
                sub_kg.add((x, y, z))
                if isinstance(z, BNode):
                    for bx, by, bz in graph.triples((z, None, None)):
                        sub_kg.add((bx, by, bz))

            conforms, infos, warnings, errors = validate_shape(
                knowledge_graph=sub_kg, shacl_shape=shape
            )
            # logger.info(
            #     f"Validation result for {s} (type: {o}): conforms={conforms}, infos={infos}, warnings={warnings}, errors={errors}"
            # )

            results[str(s)] = {
                "type": str(o),
                "ref_profile": profile["target_class"],
                "conforms": conforms,
                "infos": infos,
                "warnings": warnings,
                "errors": errors,
            }
            logger.info(f"Results for {s}: {results[str(s)]}")

            n_warnings = len(results[str(s)]["warnings"])
            n_errors = len(results[str(s)]["errors"])
            n_infos = len(results[str(s)]["infos"])
            n_profile_min_props = len(profile["mandatory_properties"])
            n_profile_rec_props = len(profile["recommended_properties"])
            n_profile_opt_props = len(profile["optional_properties"])

            completeness_score = round(
                (
                    3 * (n_profile_min_props - n_errors)
                    + 2 * (n_profile_rec_props - n_warnings)
                    + 1 * (n_profile_opt_props - n_infos)
                )
                * 100
                / (
                    3 * (n_profile_min_props)
                    + 2 * (n_profile_rec_props)
                    + 1 * (n_profile_opt_props)
                ),
                2,
            )

            results[str(s)]["completeness_score"] = completeness_score

    return results
