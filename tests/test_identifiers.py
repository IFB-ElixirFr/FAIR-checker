import unittest
import time
from pathlib import Path
from urllib.parse import urlparse
import logging
import sys
from rdflib import ConjunctiveGraph, URIRef

from metrics.F1B_Impl import F1B_Impl
from metrics.util import describe_biotools
from metrics.WebResource import WebResource

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
if not logger.handlers:
    logger.addHandler(stream_handler)


class TestingUrlPatterns(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_persistent_ids(self):
        list_known_schemes = F1B_Impl.get_known_namespaces()

        biotools = "biotools:bwa"
        doi = "doi:10.15454/P27LDX"
        # pubmed = "pubmed:23758764"
        pubmed = "pubmed:abcd"
        dataverse = (
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        datacite = "https://search.datacite.org/works/10.7892/boris.108387"

        print(list_known_schemes)
        self.assertTrue(F1B_Impl.is_known_pid_scheme(biotools, list_known_schemes))
        self.assertTrue(F1B_Impl.is_known_pid_scheme(doi, list_known_schemes))
        self.assertTrue(F1B_Impl.is_known_pid_scheme(pubmed, list_known_schemes))
        self.assertFalse(F1B_Impl.is_known_pid_scheme(dataverse, list_known_schemes))
        self.assertFalse(F1B_Impl.is_known_pid_scheme(datacite, list_known_schemes))

    def test_id_org_dump(self):
        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str(
            (base_path / "static/data/identifiers.org.dump.json").resolve()
        )
        id_org_file = Path(static_file_path)

        mod_time_before = id_org_file.stat().st_mtime
        logger.debug(
            f"Identifiers.org dump last modification time: {time.ctime(mod_time_before)}"
        )
        F1B_Impl.update_identifiers_org_dump()
        mod_time_after = id_org_file.stat().st_mtime
        logger.debug(
            f"Identifiers.org dump last modification time: {time.ctime(mod_time_after)}"
        )
        self.assertTrue(mod_time_before < mod_time_after, "the file should be modified")

    def test_external_links_KG(self):
        # url = "http://www.wikidata.org/entity/Q28665865" TODO SPARQL describe not working
        # url = "https://search.datacite.org/works/10.7892/boris.108387" TODO SPARQL describe not working
        url = "https://bio.tools/bwa"

        kg = ConjunctiveGraph()
        kg = describe_biotools(url, kg)
        # print(kg.serialize(format="turtle").decode())

        domains = []
        for s, p, o in kg:
            for term in [s, o]:
                if isinstance(term, URIRef):
                    parsed_url = urlparse(term)
                    if parsed_url.netloc not in domains:
                        domains.append(parsed_url.netloc)

        logger.info(f"Domain names found in URis: {domains}")
        self.assertGreaterEqual(
            len(domains), 6, msg=f"length of {domains} should be >= 6"
        )


if __name__ == "__main__":
    unittest.main()
