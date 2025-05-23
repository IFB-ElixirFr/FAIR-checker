# from abc import ABC, abstractmethod
# import logging

from rdflib import ConjunctiveGraph, URIRef
from rdflib.namespace import RDF
from jinja2 import Template
from pyshacl import validate

# class AbstractProfile(ABC):


class Profile:
    # TODO doc class
    # TODO getters for class attributes

    # cache = {}

    def __init__(
        self,
        shape_name,
        target_classes,
        min_props,
        rec_props,
        ref_profile,
        latest=True,
        deprecated=False,
    ):
        self.shape_name = shape_name
        self.target_classes = target_classes
        self.min_props = min_props
        self.rec_props = rec_props
        self.ref_profile = ref_profile
        self.latest = latest
        self.deprecated = deprecated

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

    def get_is_deprecated(self):
        return self.deprecated

    def get_latest_profile(self):
        return self.latest

    def gen_SHACL_from_profile(self):
        shape_name = self.shape_name
        target_classes = self.target_classes
        min_props = self.min_props
        rec_props = self.rec_props

        # print(shape_name)
        # print(target_classes)
        # print(min_props)
        # print(rec_props)

        # @prefix bsc: <https://bioschemas.org/> .
        # @prefix bsc: <https://discovery.biothings.io/view/bioschemas/> .

        shape_template = """
            @prefix fc: <https://fair-checker.france-bioinformatique.fr#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix sc: <http://schema.org/> .
            @prefix scs: <https://schema.org/> .
            @prefix bsc: <https://discovery.biothings.io/view/bioschemas/> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            @prefix edam: <http://edamontology.org/> .
            @prefix biotools: <https://bio.tools/ontology/> .
            @prefix bioschemasdrafts: <https://discovery.biothings.io/view/bioschemasdrafts/> .
            @prefix bioschemastypes: <https://discovery.biothings.io/view/bioschemastypes/> .
            @prefix bh2022GH: <https://discovery.biothings.io/view/bh2022GH/> .

            fc:{{shape_name}}
                a sh:NodeShape ;

                {% for c in target_classes %}
                sh:targetClass {{c}}, {{c.replace("sc:", "scs:")}} ;
                {% endfor %}

                {% for min_prop in min_props %}
                sh:property [
                    {% if min_prop.startswith("sc:") %}
                    sh:path [sh:alternativePath({{min_prop}} {{min_prop.replace("sc:", "scs:")}})] ;
                    {% else %}
                    sh:path {{min_prop}} ;
                    {% endif %}
                    sh:minCount 1 ;
                    sh:severity sh:Violation
                ] ;
                {% endfor %}

                {% for rec_prop in rec_props %}
                sh:property [
                    {% if rec_prop.startswith("sc:") %}
                    sh:path [sh:alternativePath({{rec_prop}} {{rec_prop.replace("sc:", "scs:")}})] ;
                    {% else %}
                    sh:path {{rec_prop}} ;
                    {% endif %}
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

        print("Evaluating: " + str(self.target_classes))
        # print(knowledge_graph.serialize(format="trig"))

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
        # print(knowledge_graph.serialize(format="turtle"))
        # print(shacl_shape)
        # print(results_text)
        # print(conforms)
        # print(results_graph.serialize(format="turtle"))
        warnings = []
        errors = []
        for r in results:
            if "#Warning" in r["severity"]:
                # print(
                #     f'WARNING: Property {r["path"]} should be provided for {r["node"]}'
                # )
                if r["path"].startswith("http://schema.org/"):
                    pass
                elif r["path"].startswith("https://schema.org/"):
                    warnings.append(f'{r["path"]}')
                else:
                    warnings.append(f'{r["path"]}')
            if "#Violation" in r["severity"]:
                # print(f'ERROR: Property {r["path"]} must be provided for {r["node"]}')
                # print(r["path"])
                if r["path"].startswith("http://schema.org/"):
                    pass
                elif r["path"].startswith("https://schema.org/"):
                    errors.append(f'{r["path"]}')
                else:
                    errors.append(f'{r["path"]}')
        # print(errors)
        # print(warnings)
        return conforms, warnings, errors

    def match_sub_kgs_from_profile(self, kg):
        # kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        # kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        # kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        sub_kg_list = []
        # print(kg.serialize(format="trig"))

        # for s, p, o in kg.triples((None, RDF.type, None)):
        for s, p, o, g in kg.quads((None, RDF.type, None, None)):
            # print(o)
            # print(o.n3(kg.namespace_manager))
            if o.n3(kg.namespace_manager).replace("scs:", "sc:") in self.target_classes:
                print(f"Trying to validate {s} as a(n) {o} resource")
                sub_kg = ConjunctiveGraph()
                sub_kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
                sub_kg.namespace_manager.bind("scs", URIRef("https://schema.org/"))
                sub_kg.namespace_manager.bind(
                    "dct", URIRef("http://purl.org/dc/terms/")
                )

                for x, y, z, g in kg.quads((s, None, None, None)):
                    # print(f"{x} -> {y} -> {z} -> {g}")
                    # print(i)
                    sub_kg.add((x, y, z))
                # print(sub_kg.serialize(format="trig"))
                sub_kg_list.append({"sub_kg": sub_kg, "subject": s, "object": o})

        return sub_kg_list

    def compute_similarity(self, kg) -> float:
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
        # print(str(self.get_name()) + " targeting -> " + str(self.get_target()))
        # print(kg.serialize(format="turtle"))

        # list classes
        for s, p, o in kg.triples((None, RDF.type, None)):
            # print()
            # print(bs_profiles.keys())
            # print(o.n3(kg.namespace_manager))
            # print(self.target_classes)
            if o.n3(kg.namespace_manager) in self.target_classes:
                # print()
                print(f"Trying to validate {s} as a(n) {o} resource")
                shacl_shape = self.gen_SHACL_from_profile()

                sub_kg = ConjunctiveGraph()
                for x, y, z in kg.triples((s, None, None)):
                    sub_kg.add((x, y, z))

                conforms, warnings, errors = self.validate_shape(
                    knowledge_graph=sub_kg, shacl_shape=shacl_shape
                )

                # print(conforms)
                # print(f"{len(errors)} / {self.nb_min}")
                # print(f"{len(warnings)} / {self.nb_rec}")

                weight = 20

                max_points = weight * self.nb_min + self.nb_rec

                similarity = (
                    max_points - (weight * len(errors) + len(warnings))
                ) / max_points
                similarity = round(similarity, 2)
                print(self.get_name() + ": " + str(similarity))
                return similarity

        return 0.0

    def compute_loose_similarity(self, kg) -> float:
        kg.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        kg.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        kg.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        print(f"Computing loose similarity  for profile {self.shape_name}")
        # print(len(kg))
        # print(kg.serialize(format="turtle"))

        # list classes
        for s, p, o in kg.triples((None, RDF.type, None)):
            has_required_rdf_type = 0
            if o.n3(kg.namespace_manager) in self.target_classes:
                has_required_rdf_type = 10

            # print()
            print(f"Trying to validate {s} as a(n) {o} resource")
            shacl_shape = self.gen_SHACL_from_profile()

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
