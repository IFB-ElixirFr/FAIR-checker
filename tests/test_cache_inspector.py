import tempfile
import unittest
from unittest import mock

from diskcache import Cache
from rdflib import URIRef

import metrics.util as util
from app import app

PORTAL_URI = "http://example.org/term"


def _key(func, *args):
    return (util.__name__, func, args)


def _portal_key(name, endpoint, query, uri):
    return _key(
        "_run_portal_ask",
        ("name", name),
        ("endpoint", endpoint),
        ("query", query),
        ("uri", uri),
    )


def _by_uri(entries):
    return {(e["registry"], e["uri"]): e for e in entries}


def _entry(registry, type_, uri, answer, hits):
    return {
        "registry": registry,
        "type": type_,
        "uri": uri,
        "answer": answer,
        "expires_in": 60,
        "hits": hits,
    }


class CacheTestCase(unittest.TestCase):
    """Base class: disk caches created in a temporary directory."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp_dir = tmp.name

    def _new_cache(self, name, **kwargs):
        cache = Cache(
            f"{self.tmp_dir}/{name}", eviction_policy="least-frequently-used", **kwargs
        )
        self.addCleanup(cache.close)
        return cache

    def _populated_cache(self):
        cache = self._new_cache("cache")
        cache.set(
            _key("ask_BioPortal", ("uri", "http://ex.org/a"), ("type", "class")),
            True,
            expire=3600,
        )
        cache.set(
            _key("ask_OLS", ("uri", "http://ex.org/b"), ("type", "property")),
            False,
            expire=3600,
        )
        cache.set(
            _portal_key(
                "LOV",
                util.LOV_SPARQL_ENDPOINT,
                util._ASK_CLASS_QUERY,
                "http://ex.org/c",
            ),
            True,
            expire=3600,
        )
        cache.set(
            _portal_key(
                "EarthPortal",
                util.EARTHPORTAL_SPARQL_ENDPOINT,
                util._ASK_CLASS_QUERY,
                PORTAL_URI,
            ),
            True,
            expire=3600,
        )
        cache.set(
            _portal_key(
                "AgroPortal",
                util.AGROPORTAL_SPARQL_ENDPOINT,
                util._ASK_PROPERTY_QUERY,
                PORTAL_URI,
            ),
            False,
            expire=3600,
        )
        # entry written with a query that is no longer the current one
        cache.set(
            _portal_key(
                "AgroPortal",
                util.AGROPORTAL_SPARQL_ENDPOINT,
                "ASK { <%s> a owl:Class }",
                "http://ex.org/old",
            ),
            False,
            expire=3600,
        )
        # not a registry lookup
        cache.set("something else", 42)
        return cache


class RegistryCacheListingTestCase(CacheTestCase):
    def setUp(self):
        super().setUp()
        self.cache = self._populated_cache()

    def test_lists_one_entry_per_registry_lookup(self):
        entries, others = util.list_registry_cache(self.cache)
        self.assertEqual(others, 2)  # the unrelated entry and the outdated-query one
        by_uri = _by_uri(entries)
        self.assertEqual(len(entries), 5)

        self.assertEqual(by_uri[("BioPortal", "http://ex.org/a")]["type"], "class")
        self.assertIs(by_uri[("BioPortal", "http://ex.org/a")]["answer"], True)
        self.assertIs(by_uri[("OLS", "http://ex.org/b")]["answer"], False)
        self.assertEqual(by_uri[("LOV", "http://ex.org/c")]["type"], "class")
        self.assertEqual(by_uri[("EarthPortal", PORTAL_URI)]["type"], "class")
        self.assertEqual(by_uri[("AgroPortal", PORTAL_URI)]["type"], "property")

    def test_entry_with_outdated_query_is_not_listed(self):
        entries, _ = util.list_registry_cache(self.cache)
        self.assertNotIn(("AgroPortal", "http://ex.org/old"), _by_uri(entries))
        self.assertTrue(all(e["type"] != "outdated query" for e in entries))

    def test_entry_cached_before_the_type_argument_is_not_listed(self):
        # ask_OLS(uri) had no type: such entries are never served again
        self.cache.set(
            _key("ask_OLS", ("uri", "http://ex.org/untyped")), True, expire=3600
        )
        entries, others = util.list_registry_cache(self.cache)
        self.assertNotIn(("OLS", "http://ex.org/untyped"), _by_uri(entries))
        self.assertEqual(others, 3)
        self.assertTrue(all(e["type"] is not None for e in entries))

    def test_expiry_is_reported_in_seconds(self):
        entries, _ = util.list_registry_cache(self.cache)
        for e in entries:
            self.assertTrue(0 < e["expires_in"] <= 3600)

    def test_hits_count_cache_reads(self):
        key = _key("ask_OLS", ("uri", "http://ex.org/b"), ("type", "property"))
        for _ in range(3):
            self.cache.get(key)
        by_uri = _by_uri(util.list_registry_cache(self.cache)[0])
        self.assertEqual(by_uri[("OLS", "http://ex.org/b")]["hits"], 3)
        self.assertEqual(by_uri[("LOV", "http://ex.org/c")]["hits"], 0)

    def test_listing_does_not_change_the_hits(self):
        key = _key("ask_OLS", ("uri", "http://ex.org/b"), ("type", "property"))
        self.cache.get(key)
        for _ in range(3):
            entries, _ = util.list_registry_cache(self.cache)
        self.assertEqual(_by_uri(entries)[("OLS", "http://ex.org/b")]["hits"], 1)

    def test_disk_cache_counts_hits(self):
        self.assertEqual(util.dcache.eviction_policy, "least-frequently-used")

    def test_empty_cache(self):
        empty = Cache(f"{self.tmp_dir}/empty")
        self.addCleanup(empty.close)
        self.assertEqual(util.list_registry_cache(empty), ([], 0))


class MostAccessedTestCase(unittest.TestCase):
    def test_one_row_per_uri(self):
        entries = [
            _entry("OLS", None, "http://ex.org/t", True, 13),
            _entry("LOV", "property", "http://ex.org/t", True, 9),
            _entry("BioPortal", "property", "http://ex.org/t", False, 9),
            _entry("OLS", None, "http://ex.org/n", True, 10),
        ]
        top = util.most_accessed_uris(entries)
        self.assertEqual([t["uri"] for t in top], ["http://ex.org/t", "http://ex.org/n"])
        self.assertEqual(top[0]["hits"], 13)  # highest across registries, not the sum
        self.assertEqual(top[0]["type"], "property")  # a registry that knows the type wins
        self.assertIsNone(top[1]["type"])

    def test_merges_uriref_and_str(self):
        # some lookups are cached with an rdflib URIRef, others with a plain str,
        # and URIRef("x") != "x" in rdflib
        entries = [
            _entry("OLS", None, URIRef("http://ex.org/t"), True, 8),
            _entry("LOV", "class", "http://ex.org/t", True, 10),
        ]
        top = util.most_accessed_uris(entries)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["hits"], 10)
        self.assertIs(type(top[0]["uri"]), str)

    def test_ignores_unused_entries_and_applies_the_limit(self):
        entries = [
            _entry("OLS", None, f"http://ex.org/{i}", True, i) for i in range(20)
        ]
        top = util.most_accessed_uris(entries, limit=5)
        self.assertEqual([t["hits"] for t in top], [19, 18, 17, 16, 15])
        unused = [_entry("OLS", None, "http://ex.org/z", True, 0)]
        self.assertEqual(util.most_accessed_uris(unused), [])


class CacheInspectorPageTestCase(CacheTestCase):
    def setUp(self):
        super().setUp()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _use_cache(self, cache):
        patcher = mock.patch.object(util, "dcache", cache)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_page_returns_200(self):
        self._use_cache(self._populated_cache())
        response = self.client.get("/cache")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"http://ex.org/a", response.data)
        self.assertIn(b"EarthPortal", response.data)

    def test_page_shows_most_accessed(self):
        cache = self._populated_cache()
        self._use_cache(cache)
        self.assertIn(b"no hits recorded yet", self.client.get("/cache").data)
        key = _portal_key(
            "LOV", util.LOV_SPARQL_ENDPOINT, util._ASK_CLASS_QUERY, "http://ex.org/c"
        )
        for _ in range(5):
            cache.get(key)
        page = self.client.get("/cache").data
        self.assertNotIn(b"no hits recorded yet", page)
        self.assertIn(b"Most accessed", page)

    def test_page_shows_long_expiry_in_days(self):
        cache = self._new_cache("long")
        cache.set(
            _key("ask_OLS", ("uri", "http://ex.org/long"), ("type", "class")),
            True,
            expire=3 * 86400 + 5 * 3600,
        )
        cache.set(
            _key("ask_OLS", ("uri", "http://ex.org/short"), ("type", "class")),
            True,
            expire=2 * 3600 + 600,
        )
        self._use_cache(cache)
        page = self.client.get("/cache").data.decode()
        # the expiry counts down while the test runs
        self.assertTrue("3 d 4 h" in page or "3 d 5 h" in page)
        self.assertIn("2 h", page)
        self.assertNotIn("77 h", page)

    def test_page_handles_empty_cache(self):
        self._use_cache(self._new_cache("empty"))
        response = self.client.get("/cache")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"empty", response.data.lower())

    def test_page_is_not_in_the_menu(self):
        self.assertNotIn(b"/cache", self.client.get("/about").data)


if __name__ == "__main__":
    unittest.main()
