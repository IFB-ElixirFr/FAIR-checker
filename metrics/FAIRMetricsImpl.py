from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.Evaluation import Evaluation
from metrics.test_metric import testMetric, requestResultSparql


class FAIRMetricsImpl(AbstractFAIRMetrics):
    """
    The implementation for FAIRMetrics from Mark D. W.

    Args:
        AbstractFAIRMetrics (AbstractFAIRMetrics): The parent abstract class
    """

    def __init__(self, name, id, desc, api, principle, creator, created_at, updated_at):
        """
        The constructor for the FAIRMetrics implementation

        Args:
            name (str): Name of the metric
            id (str): ID of the metric
            desc (str): The description of the metric
            api (str): URL of the API to make a FAIRMetrics evaluation
            principle (str): The principle to which apply the metric
            creator (str): The creator of the metric
            created_at (str): The date when the metric was created
            updated_at (str): The date when the metric was updated
        """
        self.name = name
        self.id = id
        self.desc = desc
        self.api = api
        self.implem = "FAIRMetrics"
        self.principle = principle
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at

    def get_api(self):
        """
        Get the FAIRMetrics API to evaluate the metric

        Returns:
            str: The URL of the API to evaluate the metric
        """
        return self.api

    def evaluate(self, url) -> Evaluation:
        """
        Evaluate the URL using the FAIRMetrics API and populating the Evaluation object with resulting informations from the test.

        Args:
            url (str): The URL of the web resource to be evaluated

        Returns:
            Evaluation: The Evaluation instance that contains FAIRMetrics evaluation results
        """
        data = '{"subject": "' + url + '"}'
        print("Evaluating " + self.name)

        eval = Evaluation()
        eval.set_start_time()
        eval.result_text = testMetric(self.api, data)
        eval.set_end_time()
        eval.set_score(requestResultSparql(eval.result_text, "ss:SIO_000300"))
        eval.set_reason(requestResultSparql(eval.result_text, "schema:comment"))
        # principle are URLs so we get the last element after the last /
        eval.set_metrics(self.principle.split("/")[-1])
        eval.set_target_uri(url)
        eval.persist()

        return eval

    def weak_evaluate(self):
        """
        Not supported by FAIRMetrics
        """
        pass

    def strong_evaluate(self):
        """
        Not supported by FAIRMetrics
        """
        pass
