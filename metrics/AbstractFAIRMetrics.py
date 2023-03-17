from abc import ABC, abstractmethod
import logging
import sys
from io import StringIO
from metrics.Evaluation import Result, Evaluation


class AbstractFAIRMetrics(ABC):
    """
    The AbstractFAIRMetrics class

    Args:
        ABC (ABC): Generic abstract class
    """

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
        """
        The constructor of the AbstractFAIRMetrics

        Args:
            web_resource (WebResource, optional): A WebResource that will be evaluated. Defaults to None.
        """
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
        """
        Get the name of the metric

        Returns:
            str: The name of the metric
        """
        return self.name

    # desc
    def get_desc(self):
        """
        Get the description of the metric

        Returns:
            str: The description of the metric
        """
        return self.desc

    def get_id(self):
        """
        Get the ID of the metric

        Returns:
            str: The ID of the metric
        """
        return self.id

    def get_principle(self):
        """
        Get the principle to which the metric apply

        Returns:
            str: The principle of the metric
        """
        return self.principle

    def get_principle_tag(self):
        """
        Get the principle TAG of the metric (F1A, I2, etc)

        Returns:
            str: The principle TAG of the metric
        """
        return self.principle_tag

    def get_creator(self):
        """
        Get the creator name of the metric

        Returns:
            str: The creator of the metric
        """
        return self.creator

    def get_implem(self):
        """
        Get the implementator of the metric (e.g. FAIR-Checker, FAIRMetrics, etc)

        Returns:
            str: The implementator of the metric
        """
        return self.implem

    def get_creation_date(self):
        """
        Get the creation date of the metric

        Returns:
            str: The creation date of the metric
        """
        return self.created_at

    def get_update_date(self):
        """
        Get the latest update date of the metric

        Returns:
            str: The update date of the metric
        """
        return self.updated_at

    def get_requests_status_code(self):
        """
        Get the status_code of the URL WebResource instance evaluated

        Returns:
            int: The status_code of the resource
        """
        return self.requests_status_code

    def get_web_resource(self):
        """
        Get the WebResource instance that is evaluated

        Returns:
            WebResource: The WebResource instance
        """
        return self.web_resource

    def get_evaluation(self):
        """
        Get the Evaluation instance for a metric and a specific resource

        Returns:
            Evaluation: The evaluation instance
        """
        return self.evaluation

    def set_id(self, id):
        """
        Set the ID of the FAIR metric

        Args:
            id (str): The ID of the metric
        """
        self.id = id

    def set_web_resource(self, web_resource):
        """
        Set the WebResoure using an existing instance that will be evaluated

        Args:
            web_resource (WebResource): The WebResource instance
        """
        self.web_resource = web_resource

    def set_new_evaluation(self):
        """
        Set a new instance of an evaluation
        """
        self.evaluation = Evaluation()

    def evaluate(self) -> Evaluation:
        """
        Evaluate a WebResource using the FAIR metric implementation

        Returns:
            Evaluation: The Evaluation instance completed with results and metadata informations
        """

        logging.debug(f"Evaluating metrics {self.get_name()}")
        logging.debug(f"Evaluating metrics {self.get_principle_tag()}")
        self.set_new_evaluation()
        eval = self.get_evaluation()
        eval.set_start_time()

        # logging.info(eval)
        # print(eval)

        # Check in the cache if the metrics has not been computed yet
        try:

            url = self.get_web_resource().get_url()
            eval.set_target_uri(url)
            eval.set_web_resource(self.get_web_resource())
            if url in AbstractFAIRMetrics.cache.keys():

                if self.get_principle_tag() in AbstractFAIRMetrics.cache[url].keys():
                    # logging.warning(
                    #    f"Reusing cached result from {self.get_principle_tag()}"
                    # )
                    return AbstractFAIRMetrics.cache[url][self.get_principle_tag()]
            else:
                AbstractFAIRMetrics.cache[url] = {}

            if self.strong_evaluate().get_score() == "2":
                # print("STRONG")
                self.get_evaluation().set_end_time()
                AbstractFAIRMetrics.cache[url][
                    self.get_principle_tag()
                ] = self.get_evaluation()

                return self.get_evaluation()
            elif self.weak_evaluate().get_score() == "1":
                # print("WEAK")
                self.get_evaluation().set_end_time()
                AbstractFAIRMetrics.cache[url][
                    self.get_principle_tag()
                ] = self.get_evaluation()

                return self.get_evaluation()
            else:
                # print("NO")
                self.get_evaluation().set_end_time()
                AbstractFAIRMetrics.cache[url][
                    self.get_principle_tag()
                ] = self.get_evaluation()

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
        """
        The string method that displays the metric informations.

        Returns:
            str: The string method
        """
        return (
            f"FAIR metrics {self.id} : "
            f"\n\t {self.principle} "
            f"\n\t {self.name} "
            f"\n\t {self.desc} "
            f"\n\t {self.creator} "
            f"\n\t {self.created_at} "
            f"\n\t {self.updated_at} "
        )
