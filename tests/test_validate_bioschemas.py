
import unittest


from app import app

import urllib3



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
        # self.assertEqual(24095, len(response.get_data()))

    def test_validate_wfh(self):

        response = self.app.get("/validate_bioschemas?uri=" + self.uri_wf)
        self.assertEqual(200, response.status_code)
        # self.assertEqual(22111, len(response.get_data()))
