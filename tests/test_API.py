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

    # auto generate tests for individual each metrics

    @unittest.skip("Test")
    def test_check(self):
        response = self.app.get(
            "/swagger",
            # headers={"Content-Type": "application/json"}
        )
        response2 = self.app.get(
            "/api/check/metric_A1.1/https%3A%2F%2Fbio.tools%2Fjaspar",
            # headers={"Content-Type": "application/json"}
        )
        print(response)
        print(response2)
        self.assertEqual(200, response.status_code)

    @unittest.skip("Test")
    def test_check_F1Ab(self):
        # app = create_app('app.settings.TestConfig')
        print(app.config["SERVER_IP"])

        response = requests.get(app.config["SERVER_IP"] + "/api/check/metric_A1.1/https%3A%2F%2Fbio.tools%2Fjaspar" )
        print(response.status_code)
        print(response.json())

    # @unittest.skip("Test")
    def test_check_A11(self):
        # app = create_app('app.settings.TestConfig')
        # logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metric_A1.1/https%3A%2F%2Fbio.tools%2Fjaspar",
            # headers={"Content-Type": "application/json"}
        )
        print(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(response.get_json()))

    # @unittest.skip("Test")
    def test_check_F1A(self):
        # app = create_app('app.settings.TestConfig')
        # logging.info(app.config["SERVER_IP"])
        print("toto")
        response = self.app.get(
            "/api/check/metric_F1A/https%3A%2F%2Fbio.tools%2Fjaspar",
            # headers={"Content-Type": "application/json"}
        )

        print(response.get_json())
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(response.get_json()))

    @unittest.skip("Test")
    def test_check_all(self):
        # app = create_app('app.settings.TestConfig')
        # logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metrics_all/https%3A%2F%2Fbio.tools%2Fjaspar",
            # headers={"Content-Type": "application/json"}
        )

        print(response.get_json())
        self.assertEqual(200, response.status_code)
        self.assertEqual(14, len(response.get_json()))
