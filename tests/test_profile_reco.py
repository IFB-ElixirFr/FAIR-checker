from contextlib import AbstractAsyncContextManager
import unittest
import os

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
from profiles.ProfileFactory import gen_shacl_alternatives

from metrics.WebResource import WebResource


class GenSHACLTestCase(unittest.TestCase):
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
    }

    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_reco(self):
        soft = """
        @prefix sc: <http://schema.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        _:123   rdf:type sc:SoftwareApplication ;
                sc:name "MyTool" ;
                sc:author "Someone" ;
                sc:citation "A paper" .
        """

        kg = ConjunctiveGraph()
        kg.parse(data=soft, format="turtle")

        p = Profile(
            shape_name="ComputationalTool",
            target_classes=["sc:SoftwareApplication"],
            min_props=self.bs_profiles["sc:SoftwareApplication"]["min_props"],
            rec_props=self.bs_profiles["sc:SoftwareApplication"]["rec_props"],
        )
        sim = p.compute_similarity(kg)
        print(sim)
        self.assertAlmostEquals(sim, 0.29)

    def test_pofile_factory(self):
        console = Console()

        something = """
        @prefix sc: <http://schema.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        _:123   rdf:type sc:CreativeWork ;
                sc:name "MyTool" ;
                sc:author "Someone" ;
                sc:citation "A paper" .
        """

        kg = ConjunctiveGraph()
        kg.parse(data=something, format="turtle")

        results = {}

        profiles = ProfileFactory.create_all_profiles()

        console.print(f"Loaded {len(profiles)} Bioschemas profiles")

        for p_name in profiles.keys():
            profile = profiles[p_name]
            sim = profile.compute_similarity(kg)
            results[p_name] = {"score": sim, "ref": ""}

        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1]["score"], reverse=True)
        )
        print(sorted_results)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Profile", justify="left")
        table.add_column("Similarity score", justify="right")
        table.add_column("Profile URI", justify="right", style="green")

        for hit in sorted_results.keys():
            table.add_row(
                str(hit),
                str(sorted_results[hit]["score"]),
                f"[link={sorted_results[hit]['ref']}]{sorted_results[hit]['ref']}[/link]",
            )
        console.print(table)


if __name__ == "__main__":
    unittest.main()
