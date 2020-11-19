from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.Evaluation import Evaluation
from metrics.test_metric import testMetric, requestResultSparql


class FAIRMetricsImpl(AbstractFAIRMetrics):
    def __init__(self, name, id, desc, api, principle, creator, created_at, updated_at):
        self.name = name
        self.id = id
        self.desc = desc
        self.api = api
        self.principle = principle
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at

    def get_api(self):
        return self.api

    def evaluate(self, url) -> Evaluation :
        data = '{"subject": "' + url + '"}'
        print("Evaluating " + self.name)

        eval = Evaluation()
        eval.set_start_time()
        eval.result_text = testMetric(self.api, data)
        #print(eval.result_text)
        eval.set_end_time()
        # evaluation_obj.result_json = json.loads(self.result_text)
        eval.set_score(requestResultSparql(eval.result_text, "ss:SIO_000300"))
        eval.set_reason(requestResultSparql(eval.result_text, "schema:comment"))
        eval.set_metrics(self.principle)
        eval.set_target_uri(url)
        eval.persist()

        return eval