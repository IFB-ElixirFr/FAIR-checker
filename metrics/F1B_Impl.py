import logging
import json

import requests
from pathlib import Path
from urllib.parse import urlparse
import logging
from rdflib import URIRef

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
    def is_known_pid_scheme(identifier, list_of_known_namespaces) -> bool:
        logging.debug(f"Testing ID scheme for {identifier}, ({type(identifier)})")
        parsed_url = urlparse(str(identifier))
        if not parsed_url.scheme:
            prefix = parsed_url.path.split(":")[0]
            check = prefix in list_of_known_namespaces
            logging.debug(f"{prefix} known in Identifiers.org: {check}")
        elif parsed_url.scheme in ["http", "https"]:
            check = parsed_url.netloc in list_of_known_namespaces
            logging.debug(f"{parsed_url.netloc} known in Identifiers.org: {check}")
        else:
            check = parsed_url.scheme in list_of_known_namespaces

        return check

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Persistent IDs"
        self.id = "2"
        self.principle = "https://w3id.org/fair/principles/terms/F1"
        self.principle_tag = "F1B"
        self.implem = "FAIR-Checker"
        self.desc = """
            Weak : FAIR-Checker verifies that at least one namespace from identifiers.org is used in metadata.<br><br>
            Strong : FAIR-Checker verifies that the  “identifier” property from DCTerms or Schema.org vocabularies is present in metadata. 
        """

    def weak_evaluate(self):
        """
        at least one of the RDF term (subject, predicate, or object) reuse one of the Identifiers.org namespaces
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        kg = self.get_web_resource().get_rdf()
        namespaces = F1B_Impl.get_known_namespaces()
        eval.log_info("Weak evaluation:")
        eval.log_info(
            "Checking that at least one namespace from identifiers.org is in metadata"
        )
        for s, p, o in kg:
            for term in [s, o]:
                if F1B_Impl.is_known_pid_scheme(str(term), namespaces):
                    eval.log_info(f"Found an Identifiers.org namespace for {str(term)}")
                    eval.set_score(1)
                    return eval
        eval.log_info("No namespace from identifiers.org found")
        eval.set_recommendations(
            """
            You should use a namespace that can be found in Identifiers.org
            here: https://registry.identifiers.org/registry#!
        """
        )
        eval.set_score(0)
        return eval

    def strong_evaluate(self):
        """
        dcterms:identifiers or schema:identifier and known in Identifiers.org
        """
        eval = self.get_evaluation()
        eval.set_implem(self.implem)
        eval.set_metrics(self.principle_tag)

        query_identifiers = (
            self.COMMON_SPARQL_PREFIX
            + """ 
ASK { 
    VALUES ?p {dct:identifier schema:identifier} . 
    ?s ?p ?o .
}
            """
        )
        # eval.log_info(f"Running query:" + f"\n{query_identifiers}")
        eval.log_info("Strong evaluation:")
        eval.log_info(
            "Checking if there is either schema:identifier or dct:identifier property in metadata"
        )
        res = self.get_web_resource().get_rdf().query(query_identifiers)
        for bool_res in res:
            if bool_res:
                eval.log_info("Found at least one of those property in metadata")
                eval.set_score(2)
            else:
                eval.log_info("None of those property were found in metadata")
                eval.log_info("Trying weaker evaluation")
                eval.set_score(0)
            return eval
        pass
