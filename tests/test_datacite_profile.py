import unittest
import json
from rdflib import Graph

from profiles.DataciteProfile import datacite_profile, validate_md


class DataciteProfileCompletenessTestCase(unittest.TestCase):
    def test_datacite_completeness_low_and_high_examples(self):
        low_ttl = """
        @prefix sc: <http://schema.org/> .

        <https://example.org/low>
            a sc:CreativeWork ;
            sc:name "Minimal DataCite-like record" .
        """

        high_ttl = """
        @prefix sc: <http://schema.org/> .

        <https://example.org/high>
            a sc:CreativeWork ;
            sc:identifier "doi:10.1234/example" ;
            sc:creator "Alice" ;
            sc:name "Complete DataCite-like record" ;
            sc:publisher "Example Publisher" ;
            sc:datePublished "2026-05-28" ;
            sc:about "FAIR metadata" ;
            sc:contributor "Bob" ;
            sc:dateCreated "2026-05-01" ;
            sc:isPartOf "Example Collection" ;
            sc:description "A complete synthetic metadata record" ;
            sc:spatialCoverage "EU" ;
            sc:inLanguage "en" ;
            sc:encodingFormat "text/html" ;
            sc:version "1.0" ;
            sc:license "https://creativecommons.org/licenses/by/4.0/" .
        """

        low_graph = Graph()
        low_graph.parse(data=low_ttl, format="turtle")
        low_results = validate_md(low_graph, datacite_profile)
        print(json.dumps(low_results, indent=2))
        low_score = low_results["https://example.org/low"]["completeness_score"] # type: ignore

        high_graph = Graph()
        high_graph.parse(data=high_ttl, format="turtle")
        high_results = validate_md(high_graph, datacite_profile)
        print(json.dumps(high_results, indent=2))
        high_score = high_results["https://example.org/high"]["completeness_score"] # type: ignore

        self.assertLess(low_score, 40.0)
        self.assertGreater(high_score, 90.0)
        self.assertGreater(high_score, low_score)


if __name__ == "__main__":
    unittest.main()
