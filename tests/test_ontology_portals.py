import unittest
import uuid
from unittest import mock

import requests

import metrics.util as util
from metrics.util import ask_AgroPortal, ask_EarthPortal


class AgroPortalTestCase(unittest.TestCase):
    """Live checks against the AgroPortal SPARQL endpoint."""

    def test_class_known(self):
        self.assertTrue(
            ask_AgroPortal("http://purl.obolibrary.org/obo/VBO_0200603", "class")
        )

    def test_property_known(self):
        self.assertTrue(
            ask_AgroPortal(
                "http://www.foodvoc.org/resource/FIO#hasNutrient", "property"
            )
        )

    def test_property_unknown(self):
        self.assertFalse(
            ask_AgroPortal("http://www.foodvoc.org/resource/FIO#hasNut", "property")
        )


class EarthPortalTestCase(unittest.TestCase):
    """Live checks against the EarthPortal SPARQL endpoint."""

    def test_class_known(self):
        self.assertTrue(
            ask_EarthPortal(
                "http://www.cadastralvocabulary.org/CaLAThe/PostalAddress", "class"
            )
        )

    def test_property_known(self):
        self.assertTrue(
            ask_EarthPortal(
                "http://nfdi4earth.de/ontology/isNFDI4EarthLabelled", "property"
            )
        )

    def test_property_unknown(self):
        self.assertFalse(
            ask_EarthPortal("http://nfdi4earth.de/ontology/isNFILabelled", "property")
        )


class OntologyPortalOfflineTestCase(unittest.TestCase):
    """Checks of the request/response handling, without network access."""

    @staticmethod
    def _unique_uri():
        # ask_* results are cached on disk: use fresh URIs
        return f"http://example.org/{uuid.uuid4()}"

    @staticmethod
    def _response(boolean):
        res = mock.Mock()
        res.raise_for_status.return_value = None
        res.json.return_value = {"head": {"link": []}, "boolean": boolean}
        return res

    def test_earthportal_class_query(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._response(True)
        ) as get:
            self.assertTrue(ask_EarthPortal(uri, "class"))
        args, kwargs = get.call_args
        self.assertEqual(args[0], util.EARTHPORTAL_SPARQL_ENDPOINT)
        query = kwargs["params"]["query"]
        self.assertIn("owl:Class skos:Concept", query)
        self.assertIn(f"<{uri}> rdf:type ?c_spec", query)

    def test_earthportal_property_query(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._response(False)
        ) as get:
            self.assertFalse(ask_EarthPortal(uri, "property"))
        query = get.call_args.kwargs["params"]["query"]
        self.assertIn("owl:ObjectProperty owl:DatatypeProperty", query)
        self.assertIn(f"<{uri}> rdf:type ?p_spec", query)

    def test_unreachable_registry_returns_none_and_is_not_cached(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", side_effect=requests.exceptions.ConnectionError
        ):
            self.assertIsNone(ask_AgroPortal(uri, "class"))
        # a later call must reach the (now working) registry again
        with mock.patch.object(util.requests, "get", return_value=self._response(True)):
            self.assertTrue(ask_AgroPortal(uri, "class"))

    def test_lov_uses_the_portal_queries(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._response(True)
        ) as get:
            self.assertTrue(util.ask_LOV(uri, "class"))
        args, kwargs = get.call_args
        self.assertEqual(args[0], util.LOV_SPARQL_ENDPOINT)
        self.assertIn("owl:Class skos:Concept", kwargs["params"]["query"])
        with mock.patch.object(
            util.requests, "get", return_value=self._response(False)
        ) as get:
            self.assertFalse(util.ask_LOV(uri, "property"))
        self.assertIn("owl:DatatypeProperty", get.call_args.kwargs["params"]["query"])

    def test_lov_does_not_cache_outages(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", side_effect=requests.exceptions.ConnectionError
        ):
            self.assertIsNone(util.ask_LOV(uri, "class"))
        with mock.patch.object(
            util.requests, "get", return_value=self._response(True)
        ) as get:
            self.assertTrue(util.ask_LOV(uri, "class"))
            # positive answers are cached
            self.assertTrue(util.ask_LOV(uri, "class"))
        self.assertEqual(get.call_count, 1)

    @staticmethod
    def _ols_response(total):
        res = mock.Mock(status_code=200)
        res.json.return_value = {"page": {"totalElements": total}}
        return res

    def test_ols_class_uses_the_terms_endpoint(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._ols_response(3)
        ) as get:
            self.assertTrue(util.ask_OLS(uri, "class"))
        args, kwargs = get.call_args
        self.assertEqual(args[0], "https://www.ebi.ac.uk/ols4/api/terms")
        self.assertEqual(kwargs["params"], {"iri": uri})

    def test_ols_property_uses_the_properties_endpoint(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._ols_response(0)
        ) as get:
            self.assertFalse(util.ask_OLS(uri, "property"))
        self.assertEqual(
            get.call_args.args[0], "https://www.ebi.ac.uk/ols4/api/properties"
        )

    def test_ols_class_and_property_answers_are_cached_separately(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", return_value=self._ols_response(1)
        ):
            self.assertTrue(util.ask_OLS(uri, "class"))
        with mock.patch.object(
            util.requests, "get", return_value=self._ols_response(0)
        ) as get:
            self.assertFalse(util.ask_OLS(uri, "property"))
        get.assert_called_once()

    def test_ols_outage_returns_none_and_is_not_cached(self):
        uri = self._unique_uri()
        with mock.patch.object(
            util.requests, "get", side_effect=requests.exceptions.ConnectionError
        ):
            self.assertIsNone(util.ask_OLS(uri, "class"))
        down = mock.Mock(status_code=503, text="down")
        with mock.patch.object(util.requests, "get", return_value=down):
            self.assertIsNone(util.ask_OLS(uri, "class"))
        with mock.patch.object(
            util.requests, "get", return_value=self._ols_response(2)
        ):
            self.assertTrue(util.ask_OLS(uri, "class"))

    def test_ols_unknown_type_is_rejected(self):
        with self.assertRaises(ValueError):
            util.ask_OLS(self._unique_uri(), "individual")

    def test_http_error_returns_none(self):
        res = mock.Mock()
        res.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        with mock.patch.object(util.requests, "get", return_value=res):
            self.assertIsNone(ask_EarthPortal(self._unique_uri(), "class"))

    def test_cached_answers_are_tied_to_the_query(self):
        uri = self._unique_uri()
        endpoint = util.EARTHPORTAL_SPARQL_ENDPOINT
        with mock.patch.object(
            util.requests, "get", return_value=self._response(False)
        ):
            self.assertFalse(
                util._run_portal_ask("t", endpoint, "ASK { <%s> a ?t }", uri)
            )
        # same URI, changed query: the answer cached for the old query is not reused
        with mock.patch.object(
            util.requests, "get", return_value=self._response(True)
        ) as get:
            self.assertTrue(
                util._run_portal_ask("t", endpoint, "ASK { <%s> a ?t . }", uri)
            )
        get.assert_called_once()

    def test_malformed_uri_is_not_sent(self):
        with mock.patch.object(util.requests, "get") as get:
            self.assertFalse(ask_AgroPortal("http://example.org/a> } # ", "class"))
            self.assertFalse(ask_EarthPortal("not a uri", "property"))
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
