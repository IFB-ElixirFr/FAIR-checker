import unittest
from flask import current_app
from app import app
import requests
from os import environ
import logging
from rdflib import ConjunctiveGraph
import json
import urllib3

# from flask_pymongo import PyMongo

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def list_routes():
    return ["%s" % rule for rule in app.url_map.iter_rules()]


def list_api_check():
    routes = []
    for rule in app.url_map.iter_rules():
        if str(rule).startswith("/api/check/metric_"):
            routes.append(str(rule).strip("<path:url>"))
    return routes


def list_api_inspect():
    routes = []
    for rule in app.url_map.iter_rules():
        if str(rule).startswith("/api/inspect/describe_"):
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
        for api_url in list_api_check():
            with self.subTest():
                # print("Testing: " + url)
                response = self.app.get(
                    api_url + self.url_biotools,
                )
                self.assertEqual(200, response.status_code)

    # @unittest.skip("Need fast")
    def test_check_all(self):
        # app = create_app('app.settings.TestConfig')
        # logging.info(app.config["SERVER_IP"])
        response = self.app.get(
            "/api/check/metrics_all/" + self.url_biotools,
            # headers={"Content-Type": "application/json"}
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(14, len(response.get_json()))

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

    def test_describe_individual(self):
        for api_url in list_api_inspect():
            with self.subTest():
                # print("Testing: " + url)

                # GET
                get_response = self.app.get(
                    api_url + self.url_datacite,
                )
                self.assertEqual(200, get_response.status_code)
                self.assertEqual(81, get_response.get_json()["triples_before"])
                if "/api/inspect/describe_openaire/" in api_url:
                    self.assertEqual(109, get_response.get_json()["triples_after"])
                else:
                    self.assertEqual(81, get_response.get_json()["triples_after"])

                # POST
                response = self.app.get(
                    "/api/inspect/get_rdf_metadata/" + self.url_datacite,
                )

                graph = json.dumps(response.get_json(), ensure_ascii=False)
                url = self.url_datacite

                post_response = self.app.post(
                    api_url, json={"json-ld": graph, "url": url}
                )
                self.assertEqual(200, post_response.status_code)
                self.assertEqual(81, post_response.get_json()["triples_before"])
                if "/api/inspect/describe_openaire/" in api_url:
                    self.assertEqual(109, post_response.get_json()["triples_after"])
                else:
                    self.assertEqual(81, post_response.get_json()["triples_after"])

    def test_inspect_ontologies(self):
        response = self.app.get(
            "/api/inspect/inspect_ontologies/" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.get_json()["classes"]))
        self.assertEqual(14, len(response.get_json()["properties"]))
