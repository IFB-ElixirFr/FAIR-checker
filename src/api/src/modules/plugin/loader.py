import os
import logging

class PluginLoader:

    ## TODO : verify the plugin syntax and if it match the yaml syntax. Say which plugin failed the test if
    ## it doesn't pass
    def verify_plugin_syntax(self):
        pass

    def verify_plugins_health(self):
        plugin_files = os.listdir("plugins")
        if len(plugin_files) == 0:
            logging.error("No plugin found in FAIR-Checker plugin directory. Make sure you have at least the default fair checker plugin in /src/api/src/plugins")
            quit()
        if not "default.yaml" in plugin_files:
            logging.warning(f"The default FAIR-Checker plugin wasn't found. Only the {len(plugin_files)} found in the plugin directory will be used")
        print(plugin_files)
