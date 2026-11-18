import unittest

from werkzeug.routing import RequestRedirect

from app import app


class DocsRouteTestCase(unittest.TestCase):
    """The documentation must be reachable from /docs, not only /docs/index.html.

    Regression: /docs and /docs/ returned 404. Routing is checked on the URL map
    so the test does not depend on a local Sphinx build (docs/_build is not tracked).
    """

    def setUp(self):
        self.urls = app.url_map.bind("localhost")

    def test_docs_root_is_routed(self):
        endpoint, _ = self.urls.match("/docs/")

        self.assertEqual(endpoint, "documentation_index")

    def test_docs_index_page_is_not_redirected(self):
        endpoint, args = self.urls.match("/docs/index.html")

        self.assertEqual(endpoint, "documentation")
        self.assertEqual(args, {"filename": "index.html"})

    def test_docs_without_trailing_slash_redirects_to_root(self):
        with self.assertRaises(RequestRedirect) as ctx:
            self.urls.match("/docs")

        self.assertTrue(ctx.exception.new_url.endswith("/docs/"))

    def test_docs_page_is_still_served(self):
        endpoint, args = self.urls.match("/docs/genindex.html")

        self.assertEqual(endpoint, "documentation")
        self.assertEqual(args, {"filename": "genindex.html"})
