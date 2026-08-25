
## Standard imports
import logging

## Config imports
from config.config import app

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
            app.add_url_rule(
                f"/{plugin.api_route}",
                endpoint=plugin.api_route,
                view_func=self.create_handler(plugin.api_route)
            )
        logging.info("Flask API routes generated successfully for every plugin")

