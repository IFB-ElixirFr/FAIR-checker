from abc import ABC, abstractmethod
import logging
import sys
from metrics.Evaluation import Result, Evaluation


class AbstractFAIRMetrics(ABC):

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
PREFIX pav: <http://purl.org/pav/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    """

    cache = {}

    def __init__(self, web_resource=None):
        self.name = "My name"
        self.id = "My id"
        self.desc = "My desc"
        self.implem = "My implem"
        self.principle = "My principle (an URI describing the metric)"
        self.principle_tag = "My principle TAG"
        self.creator = "My creator name"
        self.created_at = "My creation date"
        self.updated_at = "My update date"
        self.requests_status_code = "Status code for requests"
        self.web_resource = web_resource
        self.evaluation = Evaluation

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

    def get_principle_tag(self):
        return self.principle_tag

    def get_creator(self):
        return self.creator

    def get_implem(self):
        return self.implem

    def get_creation_date(self):
        return self.created_at

    def get_update_date(self):
        return self.updated_at

    def get_requests_status_code(self):
        return self.requests_status_code

    def get_web_resource(self):
        return self.web_resource

    def get_evaluation(self):
        return self.evaluation

    def set_web_resource(self, web_resource):
        self.web_resource = web_resource

    def set_new_evaluation(self):
        self.evaluation = Evaluation()

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

    def evaluate(self) -> Evaluation:
        logging.debug(f"Evaluating metrics {self.name}")

        # Check in the cache if the metrics has not been computed yet
        try:
            url = self.get_web_resource().get_url()
            if url in AbstractFAIRMetrics.cache.keys():
                if self.get_implem() in AbstractFAIRMetrics.cache[url].keys():
                    logging.warning(f"Reusing cached result from {self.get_implem()}")
                    return AbstractFAIRMetrics.cache[url][self.get_implem()]
            else:
                AbstractFAIRMetrics.cache[url] = {}


            if self.strong_evaluate().get_score() == "2":
                print("STRONG")
                AbstractFAIRMetrics.cache[url][self.get_implem()] = Result.STRONG
                self.get_evaluation().set_end_time()
                return self.get_evaluation()
            elif self.weak_evaluate().get_score() == "1":
                print("WEAK")
                AbstractFAIRMetrics.cache[url][self.get_implem()] = Result.WEAK
                self.get_evaluation().set_end_time()
                return self.get_evaluation()
            elif self.strong_evaluate().get_score() == "0" or self.weak_evaluate().get_score() == "0":
                print("NO")
                AbstractFAIRMetrics.cache[url][self.get_implem()] = Result.NO
                self.get_evaluation().set_end_time()
                return self.get_evaluation()
        except AttributeError as err:
            print(err)
            logging.warning("No web_resource set")

    @abstractmethod
    def weak_evaluate(self) -> Evaluation:
        pass

    @abstractmethod
    def strong_evaluate(self) -> Evaluation:
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
