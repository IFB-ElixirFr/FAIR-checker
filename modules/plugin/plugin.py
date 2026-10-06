class Plugin:

    def __init__(self, name, api_route, version, author, description, metrics, resource_examples = []):
        self.name = name
        self.api_route = api_route
        self.version = version
        self.author = author
        self.description = description
        self.depends_on = []

        self.metrics = metrics
        self.resource_examples = resource_examples

    def to_json(self):
        return {
            "name": self.name,
            "api_route": self.api_route,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "depends_on": self.depends_on
        }
