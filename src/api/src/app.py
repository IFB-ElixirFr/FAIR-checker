## Config imports
from config.logging import *
from config.config import *

## Route imports
from routes.base import *

## Module imports
from modules.plugin.loader import PluginLoader


plugin_loader = PluginLoader()
plugin_loader.verify_plugins_health()


## Launch the Flask App (Fair-Checker API)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=API_PORT, debug=True)
