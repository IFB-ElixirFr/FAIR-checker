import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The race happens on the first concurrent parses, so each attempt needs a fresh interpreter.
SCRIPT = textwrap.dedent("""
    import warnings
    warnings.filterwarnings("ignore")
    import threading
    import metrics  # noqa: F401  (must make SPARQL parsing thread safe)
    from rdflib import Graph

    g = Graph()
    g.parse(data="<http://a> <http://b> <http://c> .", format="turtle")
    q = (
        "PREFIX dct: <http://purl.org/dc/terms/> "
        "ASK { VALUES ?p { dct:license <http://b> } . ?s ?p ?o . }"
    )
    errors = []

    def work():
        for _ in range(40):
            try:
                list(g.query(q))
            except Exception as e:
                errors.append(repr(e))

    threads = [threading.Thread(target=work) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    print(len(errors), sorted(set(errors))[:2])
    raise SystemExit(1 if errors else 0)
""")


class SparqlThreadSafetyTestCase(unittest.TestCase):
    """
    rdflib's SPARQL parser (pyparsing) is not thread safe: concurrent first parses can raise
    "Param.postParse2() missing 1 required positional argument: 'tokenList'"
    and leave the parser broken for the whole process.
    """

    def test_concurrent_sparql_parsing(self):
        for attempt in range(10):
            res = subprocess.run(
                [sys.executable, "-c", SCRIPT],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.returncode,
                0,
                f"attempt {attempt}: concurrent SPARQL parsing failed: {res.stdout}{res.stderr[-500:]}",
            )


if __name__ == "__main__":
    unittest.main()
