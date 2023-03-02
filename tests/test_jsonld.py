import unittest
from rdflib import ConjunctiveGraph
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class JsonLDTestCase(unittest.TestCase):

    jsonld_http_context = """
{
  "@context": "http://schema.org/",
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
    """

    jsonld_https_context = """
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
    """

    jsonld_array_http_context = """
{
  "@context": ["http://schema.org/"],
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
    """

    jsonld_dict_vocab_http_context = """
{
  "@context": {"@vocab": "http://schema.org/"},
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
    """

    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        # browser = WebResource.WEB_BROWSER_HEADLESS
        # browser.quit()

    def test_http_context(self):
        kg = ConjunctiveGraph()
        kg.parse(data=self.jsonld_http_context, format="json-ld")
        self.assertEquals(len(kg), 5)
    
    def test_https_context(self):
        kg = ConjunctiveGraph()
        kg.parse(data=self.jsonld_https_context, format="json-ld")
        self.assertEquals(len(kg), 5)

    def test_array_context(self):
        kg = ConjunctiveGraph()
        kg.parse(data=self.jsonld_array_http_context, format="json-ld")
        self.assertEquals(len(kg), 5)
        
    def test_dict_context(self):
        kg = ConjunctiveGraph()
        kg.parse(data=self.jsonld_dict_vocab_http_context, format="json-ld")
        self.assertEquals(len(kg), 5)


if __name__ == "__main__":
    unittest.main()
