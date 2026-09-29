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

    def test_existing_registries_do_not_cache_outages(self):
        uri = self._unique_uri()
        down = mock.Mock(status_code=503, text="down")
        with mock.patch.object(util.requests, "get", return_value=down):
            self.assertIsNone(util.ask_LOV(uri))
        up = mock.Mock(status_code=200)
        up.json.return_value = {"boolean": True}
        with mock.patch.object(util.requests, "get", return_value=up) as get:
            self.assertTrue(util.ask_LOV(uri))
            # positive answers are cached
            self.assertTrue(util.ask_LOV(uri))
        self.assertEqual(get.call_count, 1)

    def test_http_error_returns_none(self):
        res = mock.Mock()
        res.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        with mock.patch.object(util.requests, "get", return_value=res):
            self.assertIsNone(ask_EarthPortal(self._unique_uri(), "class"))

    def test_malformed_uri_is_not_sent(self):
        with mock.patch.object(util.requests, "get") as get:
            self.assertFalse(ask_AgroPortal("http://example.org/a> } # ", "class"))
            self.assertFalse(ask_EarthPortal("not a uri", "property"))
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
