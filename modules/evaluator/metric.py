import logging


class Metric:

    def __init__(self, name, principle, description, rules = [], recommendations = []):
        self.name = name
        self.principle = principle
        self.description = description
        self.rules = []
        self.recommendations = []

    @classmethod
    def from_plugin_file_data(cls, metric):
        name = metric['name']
        principle = metric['principle']
        description = metric['description']

        return cls(name, principle, description)
