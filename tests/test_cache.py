import random
import time
import unittest

from cachetools import cached, TTLCache


def timeit(method):
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


# cache = TTLCache(maxsize=100, ttl=3600)
cache = TTLCache(maxsize=100, ttl=20)


@timeit
@cached(cache)
def long_ask(prop):
    res = random.choice([True, False])
    time.sleep(random.randint(1, 3))
    return {"property": prop, "exists": res}


class CacheTestCase(unittest.TestCase):
    def test_time_to_live_cachel(self):
        list_of_props = []
        for i in range(0, 10):
            list_of_props.append(f"prop_{i}")

        print()
        print("ITERATION 1")
        for p in list_of_props:
            res = long_ask(p)
            print(f'{res["property"]} exists ? {res["exists"]}')

        print("ITERATION 2")
        for p in list_of_props:
            res = long_ask(p)
            print(f'{res["property"]} exists ? {res["exists"]}')

        print("ITERATION 3")
        res = long_ask("prop_2")
        print(f'{res["property"]} exists ? {res["exists"]}')
        res = long_ask("prop_3")
        print(f'{res["property"]} exists ? {res["exists"]}')
        res = long_ask("prop_9")
        print(f'{res["property"]} exists ? {res["exists"]}')
        res = long_ask("prop_2")
        print(f'{res["property"]} exists ? {res["exists"]}')
        res = long_ask("prop_2")
        print(f'{res["property"]} exists ? {res["exists"]}')
        res = long_ask("prop_0")
        print(f'{res["property"]} exists ? {res["exists"]}')

        self.assertEqual(10, len(cache))
        cache.pop(("prop_8",))
        # print(cache.keys())
        for key in cache.keys():
            print(key)
        for item in cache.items():
            print(item)
        self.assertEqual(9, len(cache))
