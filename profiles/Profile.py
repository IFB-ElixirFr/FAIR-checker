# from abc import ABC, abstractmethod
# import logging

import requests

from rdflib import ConjunctiveGraph, URIRef
from rdflib.namespace import RDF
from jinja2 import Template
from pyshacl import validate
from os import environ, path

# class AbstractProfile(ABC):


class Profile:

    # TODO doc class
    # TODO getters for class attributes

    # cache = {}

    def __init__(self, shape_name, target_classes, min_props, rec_props, ref_profile):
        self.shape_name = shape_name
        self.target_classes = target_classes
        self.min_props = min_props
        self.rec_props = rec_props
        self.ref_profile = ref_profile

        self.shacl_shape = self.gen_SHACL_from_profile()

        self.nb_min = len(self.min_props)
        self.nb_rec = len(self.rec_props)

    # def set_ref_profile(self, ref_profile):
    #     self.ref_profile = ref_profile



    def get_name(self):
        return self.shape_name

    def get_target(self):
        return self.target_classes

    def get_required(self):
        return self.min_props

    def get_recommended(self):
        return self.rec_props

    def get_ref_profile(self):
        return self.ref_profile

    def get_shacl_shape(self):
        return self.shacl_shape

    def gen_SHACL_from_profile(self):
        shape_name = self.shape_name
        target_classes = self.target_classes
        min_props = self.min_props
        rec_props = self.rec_props

        # print(shape_name)
        # print(target_classes)
        # print(min_props)
        # print(rec_props)

        shape_template = """
@prefix ns: <https://fair-checker.france-bioinformatique.fr#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sc: <http://schema.org/> .
@prefix bsc: <https://bioschemas.org/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix edam: <http://edamontology.org/> .
@prefix biotools: <https://bio.tools/ontology/> .
@prefix bioschemastypes: <https://discovery.biothings.io/view/bioschemastypes/> .
@prefix bh2022GH: <https://discovery.biothings.io/view/bh2022GH/> .

ns:{{shape_name}}
    a sh:NodeShape ;
    
    {% for c in target_classes %}
    sh:targetClass  {{c}} ;
    {% endfor %}

    {% for min_prop in min_props %}
    sh:property [
        sh:path {{min_prop}} ;
        sh:minCount 1 ;
        sh:severity sh:Violation
    ] ;
    {% endfor %}

    {% for rec_prop in rec_props %}
    sh:property [
        sh:path {{rec_prop}} ;
        sh:minCount 1 ;
        sh:severity sh:Warning
    ] ;
    {% endfor %}
.
        """

        # [sh: alternativePath(ex:father ex: mother  )]

        template = Template(shape_template)
        shape = template.render(
            shape_name=shape_name,
            target_classes=target_classes,
            min_props=min_props,
            rec_props=rec_props,
        )

        return shape

    def validate_shape(self, knowledge_graph, shacl_shape):
        # print(knowledge_graph.serialize(format="turtle"))
        r = validate(
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
        )
        conforms, results_graph, results_text = r

        report_query = """
                SELECT ?node ?path ?path ?severity WHERE {
                    ?v rdf:type sh:ValidationReport ;
                    sh:result ?r .
                    ?r sh:focusNode ?node ;
                    sh:sourceShape ?s .
                    { ?s sh:path ?path ;
                    sh:severity ?severity . }
                    UNION { ?s sh:path/sh:alternativePath/rdf:rest*/rdf:first ?path ;
                    sh:severity ?severity . }
                    FILTER (! isBlank(?path))
                }
            """

        results = results_graph.query(report_query)
        # print("VALIDATION RESULTS")
        # print(results_text)
        # print(conforms)
        # print(results_graph.serialize(format="turtle"))
        warnings = []
        errors = []
        for r in results:
            if "#Warning" in r["severity"]:
                print(
                    f'WARNING: Property {r["path"]} should be provided for {r["node"]}'
                )
                warnings.append(f'{r["path"]}')
            if "#Violation" in r["severity"]:
                print(f'ERROR: Property {r["path"]} must be provided for {r["node"]}')
                errors.append(f'{r["path"]}')

        return conforms, warnings, errors

    def match_sub_kgs_from_profile(self, kg):
        kg.namespace_manager.bind("sc", URIRef("https://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        sub_kg_list = []

        for s, p, o in kg.triples((None, RDF.type, None)):
            # print(o)
            # print(o.n3(kg.namespace_manager))
            if o.n3(kg.namespace_manager) in self.target_classes:
                print(f"Trying to validate {s} as a(n) {o} resource")
                sub_kg = ConjunctiveGraph()
                for x, y, z in kg.triples((s, None, None)):
                    sub_kg.add((x, y, z))
                sub_kg_list.append({"sub_kg": sub_kg, "subject": s, "object": o})
        return sub_kg_list

    def compute_similarity(self, kg) -> float:
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        # print(len(kg))
        # print(kg.serialize(format="turtle"))

        results = {}

        # list classes
        for s, p, o in kg.triples((None, RDF.type, None)):
            # print()
            # print(f"{s.n3(kg.namespace_manager)} is a {o.n3(kg.namespace_manager)}")
            # print(bs_profiles.keys())
            # print(o.n3(kg.namespace_manager))
            if o.n3(kg.namespace_manager) in self.target_classes:
                # print()
                print(f"Trying to validate {s} as a(n) {o} resource")
                shacl_shape = self.gen_SHACL_from_profile(
                    # o.n3(kg.namespace_manager)
                )

                sub_kg = ConjunctiveGraph()
                for x, y, z in kg.triples((s, None, None)):
                    sub_kg.add((x, y, z))

                conforms, warnings, errors = self.validate_shape(
                    knowledge_graph=sub_kg, shacl_shape=shacl_shape
                )

                # print(conforms)
                # print(f"{len(errors)} / {self.nb_min}")
                # print(f"{len(warnings)} / {self.nb_rec}")

                max_points = 2 * self.nb_min + self.nb_rec

                similarity = (
                    max_points - (2 * len(errors) + len(warnings))
                ) / max_points
                similarity = round(similarity, 2)
                return similarity

        return 0.0

    def compute_loose_similarity(self, kg) -> float:
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        print(f"Computing loose similarity  for profile {self.shape_name}")
        # print(len(kg))
        # print(kg.serialize(format="turtle"))

        results = {}

        # list classes
        for s, p, o in kg.triples((None, RDF.type, None)):
            has_required_rdf_type = 0
            if o.n3(kg.namespace_manager) in self.target_classes:
                has_required_rdf_type = 10

            # print()
            print(f"Trying to validate {s} as a(n) {o} resource")
            shacl_shape = self.gen_SHACL_from_profile(
                # o.n3(kg.namespace_manager)
            )

            sub_kg = ConjunctiveGraph()
            for x, y, z in kg.triples((s, None, None)):
                sub_kg.add((x, y, z))

            conforms, warnings, errors = self.validate_shape(
                knowledge_graph=sub_kg, shacl_shape=shacl_shape
            )

            print(s)
            print(f"{self.shape_name} --> {conforms}")
            print(f"{has_required_rdf_type} / 10")
            print(f"{len(errors)} / {self.nb_min}")
            print(f"{len(warnings)} / {self.nb_rec}")

            max_points = 10 + 2 * self.nb_min + self.nb_rec

            similarity = (
                max_points - (2 * len(errors) + len(warnings) + has_required_rdf_type)
            ) / max_points
            similarity = round(similarity, 2)
            return similarity

        return 0.0

    # @abstractmethod
    # def weak_evaluate(self) -> Evaluation:
    #     pass

    # @abstractmethod
    # def strong_evaluate(self) -> Evaluation:
    #     pass

    def __str__(self):
        return (
            f"Profile: {self.shape_name}"
            f"\n\tTarget: {self.target_classes}"
            # f"\n\t {self.principle} "
            # f"\n\t {self.name} "
            # f"\n\t {self.desc} "
            # f"\n\t {self.creator} "
            # f"\n\t {self.created_at} "
            # f"\n\t {self.updated_at} "
        )
