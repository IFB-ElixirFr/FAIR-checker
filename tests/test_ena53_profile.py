import unittest
import json
from rdflib import Graph

from profiles.BiosampleProfile import ena53_profile, validate_md


class ENA53ProfileCompletenessTestCase(unittest.TestCase):
    def test_ena53_completeness_low_and_high_examples(self):
        low_ttl = """
        @prefix sc: <http://schema.org/> .

        <https://example.org/low>
            a sc:Sample ;
            sc:name "Minimal Sample" ;
            sc:additionalProperty [ sc:name "GAL" ; sc:value "Wellcome Sanger Institute" ] .
        """

        high_ttl = """
        @prefix sc: <http://schema.org/> .  

        <https://example.org/high>
            a sc:Sample ;
            sc:name "Complete ENA53 Sample" ;
            sc:identifier "SAMEA123456" ;
            sc:additionalProperty [ sc:name "organism part" ; sc:value "muscle" ] ;
            sc:additionalProperty [ sc:name "lifestage" ; sc:value "adult" ] ;
            sc:additionalProperty [ sc:name "project name" ; sc:value "Darwin Tree of Life" ] ;
            sc:additionalProperty [ sc:name "collected_by" ; sc:value "Jane Doe" ] ;
            sc:additionalProperty [ sc:name "collection date" ; sc:value "2024-01-15" ] ;
            sc:additionalProperty [ sc:name "geographic location (region and locality)" ; sc:value "Dorset, England" ] ;
            sc:additionalProperty [ sc:name "habitat" ; sc:value "temperate forest" ] ;
            sc:additionalProperty [ sc:name "sex" ; sc:value "female" ] ;
            sc:additionalProperty [ sc:name "geographic location (country and/or sea)" ; sc:value "United Kingdom" ] ;
            sc:additionalProperty [ sc:name "collecting institution" ; sc:value "Natural History Museum" ] ;
            sc:additionalProperty [ sc:name "geographic location (latitude)" ; sc:value "51.5" ] ;
            sc:additionalProperty [ sc:name "geographic location (longitude)" ; sc:value "-0.1" ] ;
            sc:additionalProperty [ sc:name "specimen_voucher" ; sc:value "NHM:E-123456" ] ;
            sc:additionalProperty [ sc:name "Latitude Start" ; sc:value "51.5" ] ;
            sc:additionalProperty [ sc:name "Longitude Start" ; sc:value "-0.1" ] ;
            sc:additionalProperty [ sc:name "Latitude End" ; sc:value "51.6" ] ;
            sc:additionalProperty [ sc:name "Longitude End" ; sc:value "-0.0" ] ;
            sc:additionalProperty [ sc:name "relationship" ; sc:value "child of" ] ;
            sc:additionalProperty [ sc:name "sample symbiont of" ; sc:value "SAMEA654321" ] ;
            sc:additionalProperty [ sc:name "symbiont" ; sc:value "Buchnera aphidicola" ] ;
            sc:additionalProperty [ sc:name "sample collection method" ; sc:value "sweep net" ] ;
            sc:additionalProperty [ sc:name "sample coordinator affiliation" ; sc:value "Wellcome Sanger Institute" ] ;
            sc:additionalProperty [ sc:name "sample same as" ; sc:value "SAMEA999" ] ;
            sc:additionalProperty [ sc:name "sample derived from" ; sc:value "SAMEA888" ] ;
            sc:additionalProperty [ sc:name "barcoding center" ; sc:value "WSI" ] ;
            sc:additionalProperty [ sc:name "tolid" ; sc:value "xbHom12345" ] ;
            sc:additionalProperty [ sc:name "identified_by" ; sc:value "John Smith" ] ;
            sc:additionalProperty [ sc:name "elevation" ; sc:value "10" ] ;
            sc:additionalProperty [ sc:name "identifier_affiliation" ; sc:value "NHM" ] ;
            sc:additionalProperty [ sc:name "original collection date" ; sc:value "2023-06-01" ] ;
            sc:additionalProperty [ sc:name "original geographic location" ; sc:value "Dorset" ] ;
            sc:additionalProperty [ sc:name "original geographic location (latitude)" ; sc:value "51.4" ] ;
            sc:additionalProperty [ sc:name "original geographic location (longitude)" ; sc:value "-0.2" ] ;
            sc:additionalProperty [ sc:name "sample coordinator" ; sc:value "Alice Brown" ] ;
            sc:additionalProperty [ sc:name "specimen_id" ; sc:value "SPEC001" ] ;
            sc:additionalProperty [ sc:name "GAL_sample_id" ; sc:value "GAL001" ] ;
            sc:additionalProperty [ sc:name "proxy voucher" ; sc:value "NHM:P-001" ] ;
            sc:additionalProperty [ sc:name "proxy biomaterial" ; sc:value "BIO001" ] ;
            sc:additionalProperty [ sc:name "bio_material" ; sc:value "BIO001" ] ;
            sc:additionalProperty [ sc:name "culture_or_strain_id" ; sc:value "STRAIN001" ] ;
            sc:additionalProperty [ sc:name "depth" ; sc:value "0" ] .
        """

        low_graph = Graph()
        low_graph.parse(data=low_ttl, format="turtle")
        low_results = validate_md(low_graph, ena53_profile)
        print(json.dumps(low_results, indent=2))
        low_score = low_results["https://example.org/low"]["completeness_score"]  # type: ignore

        high_graph = Graph()
        high_graph.parse(data=high_ttl, format="turtle")
        high_results = validate_md(high_graph, ena53_profile)
        print(json.dumps(high_results, indent=2))
        high_score = high_results["https://example.org/high"]["completeness_score"]  # type: ignore

        self.assertLess(low_score, 5.0)
        self.assertGreater(high_score, 95.0)
        self.assertGreater(high_score, low_score)


if __name__ == "__main__":
    unittest.main()
