import unittest
from flask import current_app
from app import app
import requests
from os import environ
import logging

# app = current_app._get_current_object()

class APITestCase(unittest.TestCase):

    def setUp(self):
        app.config["ENV"] = "test"
        # app.config['TESTING'] = True
        app.config.from_object("config.TestingConfig")
        self.app = app.test_client()
        

    def tearDown(self):
        print("TODO")

    def test_check_A11(self):
        # app = create_app('app.settings.TestConfig')
        logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metric_A1.1/https%3A%2F%2Fbio.tools%2Fjaspar", 
            # headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(response.get_json()))


    def test_check(self):
        # app = create_app('app.settings.TestConfig')
        logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metric_F1A/https%3A%2F%2Fbio.tools%2Fjaspar", 
            # headers={"Content-Type": "application/json"}
        )

        print(response.get_json())
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(response.get_json()))