import unittest
from metrics.WebResource import WebResource
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# LOGGER = logging.getLogger()
# if not LOGGER.handlers:
#    LOGGER.addHandler(logging.StreamHandler(sys.stdout))


class WebResourceTestCase(unittest.TestCase):
    def test_something(self):
        bwa = WebResource("http://bio.tools/bwa")
        logging.info(f"{len(bwa.rdf)} loaded RDF triples")
        self.assertGreaterEqual(len(bwa.rdf), 45)


if __name__ == "__main__":
    unittest.main()
