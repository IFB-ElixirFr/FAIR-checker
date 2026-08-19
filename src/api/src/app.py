## Config imports
from config.config import *

## Route imports
from routes.base import *

## Launch the Flask App (Fair-Checker API)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=API_PORT, debug=True)
