from abc import ABC, abstractmethod
import logging
from metrics.Evaluation import Evaluation
from metrics.util import get_disk_cache

logger = logging.getLogger(__name__)

TTL_EVAL = 60


class AbstractFAIRMetrics(ABC):

    COMMON_SPARQL_PREFIX = """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX doap: <http://usefulinc.com/ns/doap#>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX cc: <http://creativecommons.org/ns#>
PREFIX xhv: <http://www.w3.org/1999/xhtml/vocab#>
PREFIX sto: <https://w3id.org/i40/sto#>
PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX pav: <http://purl.org/pav/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
    """

    dcache = get_disk_cache()

    def __init__(self, web_resource=None):
        self.name = "My metric name"
        self.id = "My id"
        self.desc = "My desc"
        self.implem = "My implem"
        self.implem_source = "Source code of implementation"
        self.principle = "My principle (an URI describing the metric)"
        self.principle_tag = "My principle TAG"
        self.creator = "My creator name"
        self.created_at = "My creation date"
        self.updated_at = "My update date"
        self.requests_status_code = "Status code for requests"
        self.web_resource = web_resource
        self.evaluation = "My evaluation"

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

    def set_id(self, id):
        self.id = id

    def set_web_resource(self, web_resource):
        self.web_resource = web_resource

    def set_new_evaluation(self):
        self.evaluation = Evaluation()

    def evaluate(self) -> Evaluation:

        # print([cls.get_implem(self) for cls in AbstractFAIRMetrics.__subclasses__()])
        logging.debug(f"Evaluating metrics {self.get_name()}")
        logging.debug(f"Evaluating metrics {self.get_principle_tag()}")
        self.set_new_evaluation()
        eval = self.get_evaluation()
        eval.log_info(f"Evaluating metrics {self.get_name()}")
        eval.set_start_time()

        # logging.info(eval)
        # print(eval)

        # Check in the cache if the metrics has not been computed yet
        try:

            url = self.get_web_resource().get_url()
            eval.set_target_uri(url)
            eval.set_web_resource(self.get_web_resource())

            cache_key = self.get_principle_tag() + "_" + url

            if self.dcache.get(cache_key) is not None:
                logging.info(
                    f"Reusing cached result for {self.get_principle_tag()} and URL {url}"
                )
                score = self.dcache.get(cache_key)
                self.get_evaluation().set_end_time()
                self.get_evaluation().set_score(float(score))
                return self.get_evaluation()

            if self.strong_evaluate().get_score() == "2":
                self.get_evaluation().set_end_time()
                self.dcache.set(
                    cache_key, str(self.get_evaluation().get_score()), expire=TTL_EVAL
                )
                return self.get_evaluation()
            elif self.weak_evaluate().get_score() == "1":
                self.get_evaluation().set_end_time()
                self.dcache.set(
                    cache_key, str(self.get_evaluation().get_score()), expire=TTL_EVAL
                )

                return self.get_evaluation()
            else:
                self.get_evaluation().set_end_time()
                self.dcache.set(
                    cache_key, str(self.get_evaluation().get_score()), expire=TTL_EVAL
                )
                return self.get_evaluation()
        except Exception as err:
            logger.error(err)
            self.get_evaluation().set_end_time()
            self.get_evaluation().set_score(0)
            return self.get_evaluation()

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
