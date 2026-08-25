## Config imports
from config.logging import *
from config.config import *

## Route imports
from routes.base import *
from routes.generator import RouteGenerator

## Module imports
from modules.plugin.loader import PluginLoader


## Load the Fair-Checker plugins
plugin_loader = PluginLoader()
plugins = plugin_loader.load()

## Generate the API routes according each plugin characteristic
route_generator = RouteGenerator(plugins)
route_generator.generate()


## Launch the Flask App (Fair-Checker API)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=API_PORT, debug=True)
