"""Unit test: scrape a web resource and print its content."""

import unittest
from metrics.WebResource import WebResource


class TestPrintScrapedContent(unittest.TestCase):
    """Test that scraping a URL and printing its content works."""

    @unittest.skip("Skip printing scraped content in normal test runs")
    def test_print_html_content(self):
        """Scrape a known URL and print the HTML content."""
        url = "https://bio.tools/star"
        wr = WebResource(url)
        html = wr.get_html_requests()
        print(f"=== Scraped content from {url} ===")
        print(html)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 0, "Expected non-empty HTML content")


if __name__ == "__main__":
    unittest.main()
