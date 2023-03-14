import unittest
from app import app
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
            routes.append(str(rule) + "?url=")
    return routes


def list_api_inspect():
    routes = []
    for rule in app.url_map.iter_rules():
        if str(rule).startswith("/api/inspect/describe_") and str(rule).endswith("/"):
            routes.append(str(rule))
    return routes


class APITestCase(unittest.TestCase):
    url_biotools = "https://bio.tools/jaspar"
    url_datacite = "https://search.datacite.org/works/10.7892/boris.108387"
    url_workflow_hub = "https://workflowhub.eu/workflows/18"

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
            "/api/check/metrics_all?url=" + self.url_biotools,
            # headers={"Content-Type": "application/json"}
        )
        response.get_json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(11, len(response.get_json()))

    def test_inspect_get_rdf_metadata(self):
        kg = ConjunctiveGraph()
        response = self.app.get(
            "/api/inspect/get_rdf_metadata?url=" + self.url_biotools,
        )
        self.assertEqual(200, response.status_code)
        kg.parse(
            data=json.dumps(response.get_json(), ensure_ascii=False), format="json-ld"
        )
        self.assertEqual(95, len(kg))

    def test_describe_individual(self):
        for api_url in list_api_inspect():
            with self.subTest():
                # print("Testing: " + url)

                # GET
                get_api_url = api_url.rstrip("/") + "?url="
                get_response = self.app.get(
                    get_api_url + self.url_datacite,
                )
                self.assertEqual(200, get_response.status_code)
                self.assertEqual(81, get_response.get_json()["triples_before"])
                if "/api/inspect/describe_openaire" in get_api_url:
                    self.assertEqual(109, get_response.get_json()["triples_after"])
                else:
                    self.assertEqual(81, get_response.get_json()["triples_after"])

                # POST
                response = self.app.get(
                    "/api/inspect/get_rdf_metadata?url=" + self.url_datacite,
                )

                graph = json.dumps(response.get_json(), ensure_ascii=False)
                url = self.url_datacite

                post_response = self.app.post(
                    api_url, json={"json-ld": graph, "url": url}
                )
                self.assertEqual(200, post_response.status_code)
                self.assertEqual(81, post_response.get_json()["triples_before"])
                if "/api/inspect/describe_openaire" in api_url:
                    self.assertEqual(109, post_response.get_json()["triples_after"])
                else:
                    self.assertEqual(81, post_response.get_json()["triples_after"])

    def test_inspect_ontologies(self):
        response = self.app.get(
            "/api/inspect/inspect_ontologies?url=" + self.url_datacite,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.get_json()["classes"]))
        self.assertEqual(14, len(response.get_json()["properties"]))

    def test_inspect_bioschemas(self):
        response = self.app.get(
            "/api/inspect/bioschemas_validation?url=" + self.url_workflow_hub,
        )
        print(len(response.get_json()))

        results_errors_list = []
        results_warnings_list = []

        expected_errors_list = [2, 5, 5, 3, 3, 3, 3, 3, 3, 3, 3]
        expected_warnings_list = [12, 12, 11, 8, 8, 8, 8, 8, 8, 8, 8]

        result_json = response.get_json()
        for key in result_json.keys():
            results_errors_list.append(len(result_json[key]["errors"]))
            results_warnings_list.append(len(result_json[key]["warnings"]))

        self.assertCountEqual(results_errors_list, expected_errors_list)
        self.assertCountEqual(results_warnings_list, expected_warnings_list)

        self.assertEqual(200, response.status_code)
        self.assertLess(0, len(response.get_json()))

    # TODO add assertions
    def test_inspect_bioschemas_by_conformsto(self):
        response = self.app.get(
            "/api/inspect/bioschemas_validation_by_conformsto?url="
            + self.url_workflow_hub,
        )

        json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(json["https://workflowhub.eu/workflows/18?version=1"]["errors"]), 2
        )
        self.assertEqual(
            len(json["https://workflowhub.eu/workflows/18?version=1"]["warnings"]), 12
        )

    # TODO add assertions
    def test_inspect_bioschemas_by_types(self):
        response = self.app.get(
            "/api/inspect/bioschemas_validation_by_types?url=" + self.url_workflow_hub,
        )
        json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 11)
