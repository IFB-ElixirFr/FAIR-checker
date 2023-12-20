import unittest

# from rdflib import ConjunctiveGraph, Namespace, Dataset
from metrics.WebResource import WebResource
import logging

# import time
# import requests

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class SignpostingTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_turtle(self):
        turtle_WR = WebResource("https://www.w3.org/TR/turtle/examples/example1.ttl")
        logging.info(f"{len(turtle_WR.get_rdf())} loaded RDF triples")
        # self.assertEqual(60, len(turtle_WR.get_rdf()))

    def test_signposting_01(self):
        print()
        wf = WebResource(
            "https://s11.no/2022/a2a-fair-metrics/01-http-describedby-only/"
        )
        described_by = wf.retrieve_signposting_links()
        print()
        print(described_by)
        print()
        logging.info(f"{len(wf.get_rdf())} loaded RDF triples")
        print(wf.get_url())
        print(f"{len(wf.get_rdf())} loaded RDF triples")
        turtle = wf.get_rdf().serialize(format="turtle")
        print(turtle)
        # self.assertTrue("sc:ComputationalWorkflow" in turtle)


if __name__ == "__main__":
    unittest.main()
