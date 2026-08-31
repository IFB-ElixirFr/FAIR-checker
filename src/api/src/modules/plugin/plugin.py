
class Plugin:

    def __init__(self, name, api_route, version, author, description):
        self.name = name
        self.api_route = api_route
        self.version = version
        self.author = author
        self.description = description
        self.depends_on = []

        self.metrics = []
        self.resource_examples = []


