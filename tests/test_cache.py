import functools
import time
import logging
import unittest
from metrics.WebResource import WebResource
from metrics.util import get_disk_cache
from diskcache import Cache

logger = logging.getLogger(__name__)


def timeit(method):
    # wraps() keeps the attributes the wrapped callable exposes, notably the
    # __cache_key__ helper that diskcache's memoize attaches.
    @functools.wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result

    return timed


cache = Cache(directory="test_cache", default_timeout=300)


@timeit
@cache.memoize(expire=5, tag="LA")
def long_ask(prop):
    # Deterministic: the test asserts on cache behaviour, not on this value.
    res = True
    # time.sleep(random.randint(0, 2))
    time.sleep(0.3)
    return res
    # return {"property": prop, "exists": res}


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        # The disk cache is persistent across runs: start from a known state so
        # the assertions below do not depend on what a previous run left behind.
        cache.clear()

    def test_time_to_live_cachel(self):
        list_of_props = []
        for i in range(0, 5):
            list_of_props.append(f"prop_{i}")

        print(f"Cache length = {len(cache)}")
        print(f"Cache size = {round(cache.volume()/1024,2)} KB")
        cache.expire()
        print(f"Cleaned up cache")
        print(f"Cache length = {len(cache)}")
        print(f"Cache size = {cache.volume()} bytes")

        print("Number of items:", len(cache))
        print("Cache size (bytes):", cache.volume())

        print()
        print("ITERATION 1")
        for p in list_of_props:
            res = long_ask(p)
            print(f"{p} exists ? {res}")

        # Build the key via diskcache rather than hardcoding it: memoize derives
        # it from the module name, which differs depending on how the test module
        # is imported.
        self.assertIn(long_ask.__cache_key__("prop_2"), cache)
        self.assertNotIn(long_ask.__cache_key__("prop_20"), cache)

        for key in cache.iterkeys():
            print(f"Key: {key}, Value: {cache[key]}")

        print("ITERATION 2")
        for p in list_of_props:
            res = long_ask(p)
            print(f"{p} exists ? {res}")

        print("ITERATION 3")
        res = long_ask("prop_2")
        print(f"{p} exists ? {res}")

        self.assertEqual(5, len(cache))
        time.sleep(5)
        cache.expire()
        self.assertEqual(0, len(cache))

    def test_cached_web_resource(self):
        # WebResource has its own persistent disk cache, independent of the one
        # exercised above. Drop it so the first retrieval below is a real fetch.
        get_disk_cache().clear()

        start = time.time()
        wr_1 = WebResource("http://bio.tools/star")
        delta_uncached = time.time() - start
        logger.info(
            f"retrieved {len(wr_1.get_rdf())} web resource {wr_1.url} in {round(delta_uncached,2)} seconds"
        )
        self.assertGreaterEqual(len(wr_1.get_rdf()), 10)
        time.sleep(2)

        start = time.time()
        wr_2 = WebResource("http://bio.tools/star")
        delta_cached = time.time() - start
        logger.info(
            f"retrieved {len(wr_2.get_rdf())} web resource {wr_2.url} in {round(delta_cached,2)} seconds"
        )
        self.assertGreaterEqual(len(wr_2.get_rdf()), 10)
        # The cached retrieval must be materially faster than the network one.
        self.assertLess(delta_cached, delta_uncached)
