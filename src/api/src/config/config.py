
## Configuration file
##
## Load all the environment variable needed for the API to work properly
## depending on the type of environment is used as well as the flask app configuration


import os
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

## Checks if the api has been launched using docker or in standalone mode
## When the application is launched directly through the terminal, the .env file at the api of is used by flask
## and the IS_API_STANDALONE variable is read from the .env file. While if the api is launched using docker, the .env.dev file 
## present at the root of the repo is the one that docker that is used so Flask gets the the environement variable from the 
## .env.dev file instead
if "IS_API_STANDALONE" in os.environ and os.environ["IS_API_STANDALONE"] == "true":
    print("Launch in standalone mode detected")
    API_PORT = "5000"
    API_ENDPOINT = "http://localhost:5000"
    API_BASEPATH = f"graph-api"
    SPARQL_ENDPOINT = "http://localhost:7200/repositories/abromics-kg"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
else:    
    print("Launch with docker detected.")
    API_PORT = f"{os.environ['API_PORT']}"
    API_ENDPOINT = f"{os.environ['HTTP']}{os.environ['API_HOST']}:{os.environ['API_PORT']}"
    API_BASEPATH = f"{os.environ['API_BASEPATH']}"
    SPARQL_ENDPOINT = f"{os.environ['GRAPH_SERVER_HOST']}repositories/abromics-kg"
    ADMIN_USERNAME = f"{os.environ['API_ADMIN_USERNAME']}"
    ADMIN_PASSWORD = f"{os.environ['API_ADMIN_PASSWORD']}"


CACHE_DIR="cache"
QUERY_DIR="queries"


## API configuration
app = Flask(__name__)
app.config['secret_key'] = "this is secret"

config = {
    "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CORS_HEADERS": 'Content-Type'
}

app.config.from_mapping(config)
cors = CORS(app, resources={r"/*": {"origins": "*"}}) 
cache = Cache(app)

