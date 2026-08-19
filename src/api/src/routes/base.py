
## Basic api routes
##
## The basic api routes are routes that are used to get the very basic informations about the 
## API, such as its version and the queries that can be performed using the API
##
## routes:
## - [GET] home: returns a simple message
## 


from flask_cors import CORS, cross_origin
from flask import jsonify

## Config imports
from config.config import *


## Home Route
@cross_origin()
@app.route(f"/")
def home():
    return jsonify({"message": "Welcome to the Fair-Checker API"})

