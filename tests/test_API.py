import unittest
from flask import current_app
from app import app
import requests
from os import environ

# app = current_app._get_current_object()

class APITestCase(unittest.TestCase):

    def setUp(self):
        app.config["ENV"] = "test"
        # app.config['TESTING'] = True
        app.config.from_object("config.TestingConfig")
        self.app = app.test_client()
        

    def tearDown(self):
        print("TODO")

    def test_check(self):
        # app = create_app('app.settings.TestConfig')
        print(app.config["SERVER_IP"])
        response = requests.get(app.config["SERVER_IP"] + "/api/check/metric_A1.1/https%3A%2F%2Fbio.tools%2Fjaspar" )
        print(response.status_code)
        print(response.json())