import logging


class Metric:

    def __init__(self, tag, name, principle, description, recommendations = [], rules = []):
        self.tag = tag
        self.name = name
        self.principle = principle
        self.description = description
        self.recommendations = recommendations
        self.rules = [] ## will be used later for custom metrics evaluations

    @classmethod
    def from_plugin_file_data(cls, metric):
        tag = metric['tag']
        name = metric['name']
        principle = metric['principle']
        description = metric['description']
        recommendations = metric['recommendations']

        return cls(tag, name, principle, description, recommendations)
