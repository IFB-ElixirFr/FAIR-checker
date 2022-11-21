import logging
import unittest
import sys

from app import app

import urllib3

import requests


class ValidateBioschemasTestCase(unittest.TestCase):

    uri_wf = "https://workflowhub.eu/workflows/45"
    uri_tool = "https://bio.tools/bwa"

    def setUp(self):
        app.config["ENV"] = "test"
        # app.config['TESTING'] = True
        app.config.from_object("config.TestingConfig")
        self.app = app.test_client()

    def test_validate_biotools(self):

        response = self.app.get("/validate_bioschemas?uri=" + self.uri_tool)
        self.assertEqual(200, response.status_code)
        self.assertEqual(23794, len(response.get_data()))

    def test_validate_wfh(self):

        response = self.app.get("/validate_bioschemas?uri=" + self.uri_wf)
        self.assertEqual(200, response.status_code)
        self.assertEqual(21807, len(response.get_data()))
