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