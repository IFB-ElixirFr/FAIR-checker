import logging
import time
import unittest

from metrics.WebResource import WebResource

# set logger to debug
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class WebResourceV2TestCase(unittest.TestCase):
    BIOTOOLS_DATASET_URL = "https://bio.tools/bwa"
    BIOTOOLS_DATASET_API = "https://bio.tools/api/jaspar?format=jsonld"
    UNIPROT_angptl6_html = "https://www.uniprot.org/uniprotkb/Q8NI99"
    UNIPROT_angptl6_rdfxml = "https://www.uniprot.org/uniprotkb/Q8NI99.rdf"
    UNIPROT_angptl6_ttl = "https://www.uniprot.org/uniprotkb/Q8NI99.ttl"

    def test_biotools_html_retrieves_rdf_triples(self):
        start_time = time.time()
        wr = WebResource(self.BIOTOOLS_DATASET_URL)
        end_time = time.time()
        logger.info(
            f"Time taken to retrieve RDF triples: {round(end_time - start_time, 2)} seconds"
        )

        s_code = wr.get_status_code()
        logger.info(f"BIOTOOLS URL returned status code: {s_code}")

        # self.assertIsNotNone(s_code, "No HTTP status code was captured")
        # self.assertGreaterEqual(s_code, 200)
        # self.assertLess(s_code, 400)

        rdf_dataset = wr.get_rdf()

        self.assertGreater(len(rdf_dataset), 0, "No RDF triples were retrieved")

        print(rdf_dataset.serialize(format="turtle"))

    def test_biotools_api_jsonld(self):
        start_time = time.time()
        wr = WebResource(self.BIOTOOLS_DATASET_API)
        end_time = time.time()
        logger.info(
            f"Time taken to retrieve RDF triples: {round(end_time - start_time, 2)} seconds"
        )
        rdf_dataset = wr.get_rdf()
        self.assertGreater(len(rdf_dataset), 0, "No RDF triples were retrieved")
        logger.info(rdf_dataset.serialize(format="turtle"))

    def test_uniprot_html(self):
        start_time = time.time()
        wr = WebResource(self.UNIPROT_angptl6_html)
        end_time = time.time()
        logger.info(
            f"Time taken to retrieve RDF triples: {round(end_time - start_time, 2)} seconds"
        )

        rdf_dataset = wr.get_rdf()
        self.assertGreater(len(rdf_dataset), 0, "No RDF triples were retrieved")
        print(rdf_dataset.serialize(format="turtle"))

    def test_uniprot_ttl(self):
        start_time = time.time()
        wr = WebResource(self.UNIPROT_angptl6_ttl)
        end_time = time.time()
        logger.info(
            f"Time taken to retrieve RDF triples: {round(end_time - start_time, 2)} seconds"
        )

        rdf_dataset = wr.get_rdf()
        self.assertGreater(
            len(rdf_dataset), 1000, "Less than 1000 RDF triples were retrieved"
        )
        print(rdf_dataset.serialize(format="turtle"))

    def test_uniprot_rdf(self):
        start_time = time.time()
        wr = WebResource(self.UNIPROT_angptl6_rdfxml)
        end_time = time.time()
        logger.info(
            f"Time taken to retrieve RDF triples: {round(end_time - start_time, 2)} seconds"
        )

        rdf_dataset = wr.get_rdf()
        self.assertGreater(
            len(rdf_dataset), 1000, "Less than 1000 RDF triples were retrieved"
        )
        print(rdf_dataset.serialize(format="turtle"))


if __name__ == "__main__":
    unittest.main()
