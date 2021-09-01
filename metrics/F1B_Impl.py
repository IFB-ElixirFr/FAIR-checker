import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.FairCheckerExceptions import FairCheckerException


class F1B_Impl(AbstractFAIRMetrics):
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

        logging.info("Downloading Identifiers.org dump")
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
        logging.info("Identifiers.org updated")

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
        logging.debug(f"Testing ID scheme for {identifier}")
        parsed_url = urlparse(identifier)
        check = parsed_url.scheme in list_of_known_namespaces
        logging.debug(f"ID scheme in Identifiers.org: {check}")
        return check

    """
    GOAL :

    """

    def __init__(self, url):
        self.name = "F1.B"
        self.desc = ""
        self.url = url

    def weak_evaluate(self) -> bool:
        """
        at least one of the URIs reuse one of the Identifiers.org namespaces
        """

    def strong_evaluate(self) -> bool:
        """
        dcterms:identifiers or schema:identifier and known in Identifiers.org
        """
        query_identifiers = (
            self.COMMON_SPARQL_PREFIX
            + """ 
ASK { 
    VALUES ?p {dct:identifier schema:identifier} . 
    ?s ?p ?o .
}
            """
        )
        logging.debug(f"running query:" + f"\n{query_identifiers}")
        res = self.rdf_jsonld.query(query_identifiers)
        for bool_res in res:
            return bool_res
        pass
