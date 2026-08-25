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

    def _verify_plugin_compliance(self):
        self.plugin_validator.verify_plugins_compliance()

    def load(self):
        self._verify_plugin_compliance()
        pass

    
