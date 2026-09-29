import logging
import unittest

import requests
from rdflib import URIRef

from metrics.WebResource import WebResource

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ContentNegotiationTestCase(unittest.TestCase):
    # @unittest.skip("Skipping test")
    def test_uniprot_rdf_content(self):
        # use requests to get the RDF content from uniprot through content negotiation
        r = requests.get(
            "http://purl.uniprot.org/uniprot/P05067",
            # headers={"Accept": "application/rdf+xml"},
            headers={"Accept": "text/turtle"},
        )
        if r.status_code != 200:
            self.fail("Failed to get RDF content from UniProt")
        else:
            rdf_content = r.text
            logging.debug("RDF content retrieved from UniProt:")
            logging.debug(rdf_content)
            self.assertIn(
                "citation:7913895",
                rdf_content,
                "RDF content should contain the citation:7913895 citation",
            )

    # @unittest.skip("Skipping test")
    def test_uniprot_rdf_fc(self):
        url = "http://purl.uniprot.org/uniprot/P05067"

        # use request to get the RDF content from uniprot through content negotiation
        req = requests.get(
            url,
            headers={"Accept": "text/turtle"},
            timeout=10,
        )
        # logging.info(f"HTTP response status code: {req.status_code}")
        # logging.info(f"HTTP response headers: {req.headers}")
        # logging.info(f"HTTP response content: {req.text}")
        self.assertIn(
            "citation:7913895",
            req.text,
            "RDF content should contain the citation:7913895 citation",
        )

        wr = WebResource("http://purl.uniprot.org/uniprot/P05067")
        kg = wr.get_rdf()
        logging.info(f"{len(kg)} RDF triples retrieved from UniProt")
        # logging.info(kg.serialize(format="turtle"))
        # self.assertGreater(
        #     len(kg),
        #     20,
        #     "the kg should contain more than 20 triples retrieved from UniProt",
        # )

        logging.info(kg.subjects())
        self.assertIn(
            URIRef("http://purl.uniprot.org/citations/7913895"),
            kg.subjects(),
            "the kg should contain the citations:7913895 citation",
        )

    @unittest.skip(
        "Exercises the deployed instance rather than this working copy, so it "
        "fails whenever production lags behind the branch."
    )
    def test_fc_api_content_negotiation(self):
        u = "http://purl.uniprot.org/citations/7913895"
        FC_get_md = "https://fair-checker.france-bioinformatique.fr/api/inspect/get_rdf_metadata"

        res = requests.get(url=FC_get_md, params={"url": u}, timeout=10)
        logging.info(f"FC API response status code: {res.status_code}")
        logging.info(f"FC API response headers: {res.headers}")
        logging.info(f"FC API response content: {res.text}")

        self.assertIn(
            "https://www.sib.swiss/alan-bridge-group/",
            res.text,
            "alan-bridge-group should be in the JSON-LD response",
        )
