## Standard imports
import os
import sys
import yaml
import json
import logging
from jsonschema import validate
from jsonschema.exceptions import ValidationError


class PluginValidator:


    def __init__(self, plugin_directory="plugins/", plugin_schema_directory=""):
        self.plugin_directory = plugin_directory
        self.plugin_schema_directory = plugin_schema_directory
        try:
            with open(f"{plugin_schema_directory}schema.json", "r") as f:
                self.plugin_schema = json.load(f)
                logging.debug(f"Found plugin schema file in '{plugin_schema_directory}schema.json'")
                logging.debug(f"Plugin schema file in '{plugin_schema_directory}schema.json' was read and loaded successfully")
        except FileNotFoundError:
            logging.error(
                f"Plugin schema file is missing in '{plugin_schema_directory}schema.json', "
                f"impossible to verify plugins compliance with the Fair-Checker app"
            )
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(
                f"Plugin schema file in '{plugin_schema_directory}schema.json' contains a syntax error:\n\t{e}"
            )
            sys.exit(1)



    def verify_plugin_presence(self):
        plugin_files = os.listdir(self.plugin_directory)
        if len(plugin_files) == 0:
            logging.error(
                f"No plugin found in FAIR-Checker plugin directory. Make sure you have at least "
                f"the default fair checker plugin in '{self.plugin_directory}'"
            )
            sys.exit(1)
        if not "default.yaml" in plugin_files:
            plugin_filenames = "', '".join(plugin_files)
            logging.warning(
                f"The default FAIR-Checker plugin wasn't found. Only the '{plugin_filenames}' found "
                f"in the plugin directory will be used"
            ) 



    def verify_yaml_syntax(self, filename):
        with open(f"{self.plugin_directory}{filename}", "r", encoding="utf-8") as f:
            try:
                yaml.safe_load(f)
                logging.debug(f"Plugin '{self.plugin_directory}{filename}' contains valid yaml")
            except yaml.YAMLError as e:
                mark = getattr(e, "problem_mark", None)
                logging.error(
                    f"Plugin at '{self.plugin_directory}{filename}' contains a yaml syntax error: \n"
                    f"\tInvalid YAML syntax at line {mark.line + 1}, "
                    f"column {mark.column + 1}"
                )
                sys.exit(1)



    def verify_plugin_format(self, filename):
        try:
            with open(f"{self.plugin_directory}{filename}", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            validate(data, self.plugin_schema)
            logging.debug(f"Plugin '{self.plugin_directory}{filename}' is compliant with Fair-Checker plugin schema")
        except ValidationError as e:
            logging.error(
                f"Plugin '{self.plugin_directory}{filename}' is not compliant with the Fair-Checker plugin schema:\n\t{e}"
            )
            sys.exit(1)


    ## Todo: verify if there is no values that should be unique to a plugin identical
    ##       as an other loaded plugin. Unique fields includes name and api_route for instance
    def verify_plugin_mendatory_unique_values(self, filename):
        pass
        

    ## Todo: verify the values indicated for each key within the plugin
    def verify_plugin_values(self, filename):
        pass


    def verify_plugins_compliance(self):
        self.verify_plugin_presence()
        plugin_files = os.listdir(self.plugin_directory)
        for plugin_file in plugin_files:
            self.verify_yaml_syntax(plugin_file)
            self.verify_plugin_format(plugin_file)
            self.verify_plugin_values(plugin_file)
        plugin_filenames = "', '".join(plugin_files)
        logging.info(f"Plugins '{plugin_filenames}' detected and compliant with Fair-Checker plugin schema")
    
