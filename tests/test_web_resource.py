import unittest
from metrics.WebResource import WebResource
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class WebResourceTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_biotools(self):
        bwa = WebResource("http://bio.tools/bwa")
        logging.info(f"{len(bwa.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(bwa.get_rdf()), 124)

    def test_dataverse(self):
        dataverse = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        logging.info(f"{len(dataverse.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(dataverse.get_rdf()), 9)

    def test_workflowhub(self):
        bwa = WebResource("https://workflowhub.eu/workflows/263")
        logging.info(f"{len(bwa.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(bwa.get_rdf()), 29)
        turtle = bwa.get_rdf().serialize(format="turtle")
        self.assertTrue("sc:ComputationalWorkflow" in turtle)


if __name__ == "__main__":
    unittest.main()
