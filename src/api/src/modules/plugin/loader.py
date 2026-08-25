## Standard imports
import os
import sys
import yaml
import logging

## Module imports
from modules.plugin.plugin import Plugin
from modules.plugin.validator import PluginValidator


## PluginLoader class
##
## Allows to read the plugin directory and verify if their format, syntax 
## and the values each plugin contains is compliant with the Fair-Checker
## plugin standard. Also display verbose error to sdt::out when a 
## verification step failed
##
class PluginLoader:

    def __init__(self):
        self.plugin_directory = "plugins/"
        self.plugin_schema_directory = "modules/plugin/"
        self.plugin_validator = PluginValidator(plugin_directory=self.plugin_directory, plugin_schema_directory=self.plugin_schema_directory)
        self.plugins = []

    def load(self):
        self.plugin_validator.verify_plugins_compliance()
        plugin_files = os.listdir(self.plugin_directory)
        for plugin_file in plugin_files:
            try:
                with open(f"{self.plugin_directory}{plugin_file}") as f:
                    plugin_data = yaml.safe_load(f)
                    plugin = Plugin(
                        plugin_data['name'],
                        plugin_data['api_route'],
                        plugin_data['version'],
                        plugin_data['author'],
                        plugin_data['description']
                    )
                    self.plugins.append(plugin)
            except Exception as e:
                logging.error(f"Error occured when parsing the plugin file into the Plugin python class:\n\t{e}")
                sys.exit(1)
        return self.plugins
