from test_metric import getMetrics, testMetric
from evaluation import Evaluation

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

    def evaluate(self, url):
        data = '{"subject": "' + url + '"}'
        print("Evaluating " + self.name)
        evaluation_obj = Evaluation(self.api, data)
        evaluation_obj.evaluate()
        # result = testMetric(self.api, data)
        print(evaluation_obj.get_test_time())
        print(evaluation_obj)
        print(evaluation_obj.get_score())


#########################
class FAIRMetricsFactory:
    def get_metric(self, name, id, desc, api, principle, creator, created_at, updated_at):
        if name == 'test_f1':
            return F1Impl()
        elif name == 'test_r2':
            return R2Impl()
        else:
            return FAIRMetricsImpl(name, id, desc, api, principle, creator, created_at, updated_at)



json_metrics = getMetrics()



factory = FAIRMetricsFactory()

metrics = []
#for i in range(1,3):
try:
    # metrics.append(factory.get_metric("test_f1"))
    # metrics.append(factory.get_metric("test_r2"))

    for metric in json_metrics:
        # remove "FAIR Metrics Gen2" from metric name
        name = metric["name"].replace('FAIR Metrics Gen2- ','')
        # same but other syntax because of typo
        name = name.replace('FAIR Metrics Gen2 - ','')
        principle = metric["principle"].rsplit('/', 1)[-1]
        metrics.append(factory.get_metric(
            name,
            metric["@id"],
            metric["description"],
            metric["smarturl"],
            principle,
            metric["creator"],
            metric["created_at"],
            metric["updated_at"],
        ))
        # retrieve more specific info about each metric
        # metric_info = processFunction(getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
        # retrieve the name (principle) of each metric (F1, A1, I2, etc)
        # principle = metric_info["principle"].rsplit('/', 1)[-1]
        # principle = metric_info["principle"]
        # get the description on the metric
        # description = '"' + metric_info["description"] + '"'    #metrics.append(factory.get_metrics("f2"))

except ValueError as e:
    print(f"no metrics implemention for {e}")

for m in metrics:
    print(m.get_principle())
    print(m.get_name())
    # print(m.get_api())
    # m.get_desc()
    m.evaluate("http://bio.tools/bwa")
