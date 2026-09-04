
## Standard imports
import logging

## Config imports
from config.config import app, swagger_check_api_namespace

## Module imports
from modules.plugin.plugin import Plugin


## A class that allows to create flask API routes specific to each plugin
class RouteGenerator:
    
    def __init__(self, plugins):
        self.plugins = plugins

    def create_handler(self, name):
        def handler():
            return f"Hello {name}!"
        return handler

    def generate(self):
        for plugin in self.plugins:
            logging.debug(f"Creating the route for the metrics of {plugin.name}")
            for metric in plugin.metrics:
                ## Check this web page for the documentation about add_url_rule : https://flask.palletsprojects.com/en/stable/api/
                app.add_url_rule(
                    f"/{plugin.api_route}/check/metric_{metric.name}",
                    endpoint=f"/{plugin.api_route}/check/metric_{metric.name}",
                    view_func=self.create_handler(f"/{plugin.api_route}/check/metric_{metric.name}")
                )
        logging.info("Flask API routes generated successfully for every plugin")

