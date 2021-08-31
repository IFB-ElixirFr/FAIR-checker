import json
import unittest
import time
from email import message

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
import sys
from rdflib import Graph, ConjunctiveGraph, Namespace, URIRef, Literal, BNode

from metrics.FairCheckerExceptions import FairCheckerException
from metrics.util import (
    describe_opencitation,
    describe_wikidata,
    describe_loa,
    describe_biotools,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestingUrlPatterns(unittest.TestCase):
    @staticmethod
    def update_identifiers_org_dump():
        api_url = (
            "https://registry.api.identifiers.org/resolutionApi/getResolverDataset"
        )
        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str(
            (base_path / "static/data/identifiers.org.dump.json").resolve()
        )

        id_org_file = Path(static_file_path)
        mod_time_before = id_org_file.stat().st_mtime

        logger.info("Downloading Identifiers.org dump")
        id_org_resp = requests.get(api_url)
        id_org = id_org_resp.json()

        if id_org_resp.status_code == 200:
            with open(id_org_file, "w") as json_file:
                json.dump(id_org, fp=json_file)

            mod_time_after = id_org_file.stat().st_mtime
            if not (mod_time_before < mod_time_after):
                raise FairCheckerException(
                    f"Could not download dump from Identifiers.org API at {api_url}"
                )
        else:
            raise FairCheckerException(
                f"Could not download dump from Identifiers.org API at {api_url}, \nHTTP error {id_org_resp.status_code}"
            )
        logger.info("Identifiers.org updated")

    @staticmethod
    def get_known_namespaces():
        base_path = Path(__file__).parent.parent  # current directory
        static_file_path = str(
            (base_path / "static/data/identifiers.org.dump.json").resolve()
        )
        ids = []
        with open(static_file_path) as json_file:
            data = json.load(json_file)
            for n in data["payload"]["namespaces"]:
                ids.append(n["prefix"])
        return ids

    @staticmethod
    def is_known_id_scheme(identifier, list_of_known_namespaces):
        logger.debug(f"Testing ID scheme for {identifier}")
        parsed_url = urlparse(identifier)
        check = parsed_url.scheme in list_of_known_namespaces
        logger.debug(f"ID scheme in Identifiers.org: {check}")
        return check

    def test_persistent_ids(self):
        list_known_schemes = self.get_known_namespaces()

        biotools = "biotools:bwa"
        doi = "doi:10.15454/P27LDX"
        dataverse = (
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        datacite = "https://search.datacite.org/works/10.7892/boris.108387"

        self.assertTrue(self.is_known_id_scheme(biotools, list_known_schemes))
        self.assertTrue(self.is_known_id_scheme(doi, list_known_schemes))
        self.assertFalse(self.is_known_id_scheme(dataverse, list_known_schemes))
        self.assertFalse(self.is_known_id_scheme(datacite, list_known_schemes))

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
        TestingUrlPatterns.update_identifiers_org_dump()
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
                    if not parsed_url.netloc in domains:
                        domains.append(parsed_url.netloc)

        logger.info(f"Domain names found in URis: {domains}")
        self.assertGreaterEqual(
            len(domains), 6, msg=f"length of {domains} should be >= 6"
        )


if __name__ == "__main__":
    unittest.main()
