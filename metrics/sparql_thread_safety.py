"""
rdflib parses SPARQL with pyparsing, whose parse actions are not thread safe: when several
threads parse queries at the same time (metrics are evaluated concurrently by the web app),
pyparsing can raise errors such as
"Param.postParse2() missing 1 required positional argument: 'tokenList'"
and stay broken until the process restarts.

Only the parsing step needs to be serialized, query execution stays concurrent.
"""

import functools
import threading

import rdflib.plugins.sparql.processor as sparql_processor

_parse_lock = threading.RLock()


def _serialized(parse):
    @functools.wraps(parse)
    def locked_parse(*args, **kwargs):
        with _parse_lock:
            return parse(*args, **kwargs)

    return locked_parse


def install():
    for name in ("parseQuery", "parseUpdate"):
        parse = getattr(sparql_processor, name)
        if not hasattr(parse, "__wrapped__"):
            setattr(sparql_processor, name, _serialized(parse))


install()
