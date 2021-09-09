from abc import ABC, abstractmethod
import logging
import sys
from metrics.Evaluation import Result


class AbstractFAIRMetrics(ABC):

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER = logging.getLogger()
    if not LOGGER.handlers:
        LOGGER.addHandler(logging.StreamHandler(sys.stdout))

    COMMON_SPARQL_PREFIX = """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX doap: <http://usefulinc.com/ns/doap#>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX cc: <http://creativecommons.org/ns#>
PREFIX xhv: <http://www.w3.org/1999/xhtml/vocab#>
PREFIX sto: <https://w3id.org/i40/sto#>
PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>
PREFIX prov: <http://www.w3.org/ns/prov#>
    """

    def __init__(self, web_resource):
        self.name = "My name"
        self.id = "My id"
        self.desc = "My desc"
        self.principle = "My principle"
        self.creator = "My creator name"
        self.created_at = "My creation date"
        self.updated_at = "My update date"
        self.requests_status_code = "Status code for requests"
        self.web_resource = web_resource

    # name
    def get_name(self):
        return self.name

    # desc
    def get_desc(self):
        return self.desc
        # print(f'Description: {self.desc}')

    def get_id(self):
        return self.id

    def get_principle(self):
        return self.principle

    def get_creator(self):
        return self.creator

    def get_creation_date(self):
        return self.created_at

    def get_update_date(self):
        return self.updated_at

    def get_requests_status_code(self):
        return self.requests_status_code

    def get_web_resource(self):
        return self.web_resource

    # @staticmethod
    # def extract_html_requests(url):
    #     while True:
    #         try:
    #             response = requests.get(url=url, timeout=10)
    #             break
    #         except SSLError:
    #             time.sleep(5)
    #         except requests.exceptions.Timeout:
    #             print("Timeout, retrying")
    #             time.sleep(5)
    #         except requests.exceptions.ConnectionError as e:
    #             print(e)
    #             print("ConnectionError, retrying...")
    #             time.sleep(10)
    #
    #     # self.requests_status_code = response.status_code
    #     # self.html_source = response.content
    #     return response.content, response.status_code
    #
    # def extract_rdf(self):
    #     html_source = self.html_source
    #     data = extruct.extract(
    #         html_source, syntaxes=["microdata", "rdfa", "json-ld"], errors="ignore"
    #     )
    #     kg = ConjunctiveGraph()
    #
    #     base_path = Path(__file__).parent.parent  ## current directory
    #     static_file_path = str((base_path / "static/data/jsonldcontext.json").resolve())
    #
    #     # kg = util.get_rdf_selenium(uri, kg)
    #
    #     for md in data["json-ld"]:
    #         if "@context" in md.keys():
    #             print(md["@context"])
    #             if ("https://schema.org" in md["@context"]) or (
    #                 "http://schema.org" in md["@context"]
    #             ):
    #                 md["@context"] = static_file_path
    #         kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    #     for md in data["rdfa"]:
    #         if "@context" in md.keys():
    #             if ("https://schema.org" in md["@context"]) or (
    #                 "http://schema.org" in md["@context"]
    #             ):
    #                 md["@context"] = static_file_path
    #         kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    #     for md in data["microdata"]:
    #         if "@context" in md.keys():
    #             if ("https://schema.org" in md["@context"]) or (
    #                 "http://schema.org" in md["@context"]
    #             ):
    #                 md["@context"] = static_file_path
    #         kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    #
    #     self.LOGGER.debug(kg.serialize(format="turtle").decode())
    #     self.rdf_jsonld = kg

    def evaluate(self) -> Result:
        logging.debug(f"Evaluating metrics {self.name}")
        if self.strong_evaluate():
            return Result.STRONG
        elif self.weak_evaluate():
            return Result.WEAK
        else:
            return Result.NO

    @abstractmethod
    def weak_evaluate(self) -> bool:
        pass

    @abstractmethod
    def strong_evaluate(self) -> bool:
        pass

    def __str__(self):
        return (
            f"FAIR metrics {self.id} : "
            f"\n\t {self.principle} "
            f"\n\t {self.name} "
            f"\n\t {self.desc} "
            f"\n\t {self.creator} "
            f"\n\t {self.created_at} "
            f"\n\t {self.updated_at} "
        )
