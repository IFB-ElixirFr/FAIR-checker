from functools import lru_cache, wraps
from datetime import datetime, timedelta
import random
import time
import requests
import unittest

# cache = dict()

# def get_article_from_server(url):
#     print("Fetching article from server...")
#     response = requests.get(url)
#     return response.text


# def get_article(url):
#     print("Getting article...")
#     if url not in cache:
#         cache[url] = get_article_from_server(url)

#     return cache[url]


# get_article("https://realpython.com/sorting-algorithms-python/")
# get_article("https://realpython.com/sorting-algorithms-python/")


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


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


# @lru_cache(maxsize=2)
@timed_lru_cache(8)
@timeit
def long_ask():
    result = random.choice([True, False])
    time.sleep(3)
    return result


class CacheTestCase(unittest.TestCase):
    def test_cache(self):
        print()
        print(f"Result = {long_ask()}")
        time.sleep(2)
        print(f"Result = {long_ask()}")
        time.sleep(2)
        print(f"Result = {long_ask()}")
        time.sleep(2)
        print(f"Result = {long_ask()}")
        time.sleep(2)
        print(f"Result = {long_ask()}")
        time.sleep(2)
        print(f"Result = {long_ask()}")
