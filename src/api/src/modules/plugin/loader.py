import os
import sys
import yaml
import logging



class InvalidYamlError(Exception):
    pass

class PluginLoader:

    def __init__(self):
        self.plugin_directory = "plugins"

    ## TODO : verify the plugin syntax and if it match the yaml syntax. Say which plugin failed the test if
    ## it doesn't pass
    def _verify_plugin_syntax(self, filepath):
        with open(f"{self.plugin_directory}/{filepath}", "r", encoding="utf-8") as f:
            try:
                yaml.safe_load(f)
                return True
            except yaml.YAMLError as e:
                mark = getattr(e, "problem_mark", None)
                logging.error(
                    f"Plugin at '{self.plugin_directory}/{filepath}' contains a yaml syntax error: \n"
                    f"\tInvalid YAML syntax at line {mark.line + 1}, "
                    f"column {mark.column + 1}"
                )
                sys.exit(1)

    def verify_plugins_health(self):
        plugin_files = os.listdir(self.plugin_directory)
        if len(plugin_files) == 0:
            logging.error(
                f"No plugin found in FAIR-Checker plugin directory. Make sure you have at least "
                f"the default fair checker plugin in '{self.plugin_directory}/{filepath}'"
            )
            sys.exit(1)
        if not "default.yaml" in plugin_files:
            logging.warning(
                f"The default FAIR-Checker plugin wasn't found. Only the {len(plugin_files)} found "
                f"in the plugin directory will be used"
            )
        for plugin_file in plugin_files:
            if not self._verify_plugin_syntax(plugin_file):
                print(plugin_files)

