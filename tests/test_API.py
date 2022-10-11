import unittest
from flask import current_app
from app import app
import requests
from os import environ
import logging
from rdflib import ConjunctiveGraph
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def list_routes():
    return ["%s" % rule for rule in app.url_map.iter_rules()]


def list_api_check():
    routes = []
    for rule in app.url_map.iter_rules():
        if str(rule).startswith("/api/check/metric_"):
            routes.append(str(rule).strip("<path:url>"))
    return routes


class APITestCase(unittest.TestCase):
    url_biotools = "https://bio.tools/jaspar"
    url_datacite = "https://search.datacite.org/works/10.7892/boris.108387"

    def setUp(self):
        app.config["ENV"] = "test"
        # app.config['TESTING'] = True
        app.config.from_object("config.TestingConfig")
        self.app = app.test_client()

    # def tearDown(self):
    #     print("TODO")

    def test_check_individual(self):
        for url in list_api_check():
            with self.subTest():
                print("Testing: " + url)
                response = self.app.get(
                    url + self.url_biotools,
                    # headers={"Content-Type": "application/json"}
                )
                self.assertEqual(200, response.status_code)

    # @unittest.skip("Need fast")
    def test_check_all(self):
        # app = create_app('app.settings.TestConfig')
        # logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metrics_all/https%3A%2F%2Fbio.tools%2Fjaspar",
            # headers={"Content-Type": "application/json"}
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(14, len(response.get_json()))

    def test_inspect_describe_openaire(self):
        response = self.app.get(
            "/api/inspect/describe_openaire/" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(81, response.get_json()["triples_before"])
        self.assertEqual(109, response.get_json()["triples_after"])

    def test_inspect_describe_opencitation(self):
        response = self.app.get(
            "/api/inspect/describe_opencitation/" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(81, response.get_json()["triples_before"])
        self.assertEqual(81, response.get_json()["triples_after"])

    def test_inspect_describe_wikidata(self):
        response = self.app.get(
            "/api/inspect/describe_wikidata/" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(81, response.get_json()["triples_before"])
        self.assertEqual(81, response.get_json()["triples_after"])

    def test_inspect_get_rdf_metadata(self):
        kg = ConjunctiveGraph()
        response = self.app.get(
            "/api/inspect/get_rdf_metadata/" + self.url_biotools,
        )
        self.assertEqual(200, response.status_code)
        kg.parse(
            data=json.dumps(response.get_json(), ensure_ascii=False), format="json-ld"
        )
        self.assertEqual(98, len(kg))

    def test_inspect_ontologies(self):
        response = self.app.get(
            "/api/inspect/inspect_ontologies/" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.get_json()["classes"]))
        self.assertEqual(14, len(response.get_json()["properties"]))
