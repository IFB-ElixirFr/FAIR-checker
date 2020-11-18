from metrics.test_metric import getMetrics, testMetric, requestResultSparql
from metrics.evaluation import Evaluation

from abc import ABC, abstractmethod

#########################
class AbstractFAIRMetrics(ABC):
    def __init__(self):
        self.name = "My name"
        self.id = "My id"
        self.desc = "My desc"
        self.principle = "My principle"
        self.creator = "My creeator name"
        self.created_at = "My creation date"
        self.updated_at = "My update date"


    #common functionality
    def common(self):
        print('In common method of Parent')

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

    # not all metrics can have an api
    @abstractmethod
    def get_api(self):
        pass

    # evaluations are not done the same way
    @abstractmethod
    def evaluate(self):
        pass

    def __str__(self):
        return f"FAIR metrics {self.id} : " \
               f"\n\t {self.principle} " \
               f"\n\t {self.name} " \
               f"\n\t {self.desc} " \
               f"\n\t {self.creator} " \
               f"\n\t {self.created_at} " \
               f"\n\t {self.updated_at} "

#########################
class F1Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "F1"

    def evaluate(self):
        print("Evaluating F1")

#########################
class R2Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "R2"

    def evaluate(self):
        print("Evaluating R2")

#########################
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

        return eval


#########################
class FAIRMetricsFactory:
    def get_metric(self, name, id, desc, api, principle, creator, created_at, updated_at):
        if name == 'test_f1':
            return F1Impl()
        elif name == 'test_r2':
            return R2Impl()
        else:
            return FAIRMetricsImpl(name, id, desc, api, principle, creator, created_at, updated_at)



