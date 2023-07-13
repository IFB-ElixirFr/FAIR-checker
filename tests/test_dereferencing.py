import unittest
from metrics.WebResource import WebResource
import logging
import requests

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DerefTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    @unittest.skip("Failing redirect")
    def test_redirect2(self):
        response = requests.get("http://ns.inria.fr/covid19/covidontheweb-1-2")
        print(response.status_code)
        print(response.text)

        for resp in response.history:
            print(resp.status_code, " | ", resp.url)

    @unittest.skip("Failing redirect")
    def test_redirect(self):
        wr1 = WebResource("http://ns.inria.fr/covid19/covidontheweb-1-2")
        kg1 = wr1.get_rdf()
        print(kg1.serialize(format="turtle"))
        # self.assertEquals(len(kg), 19, "the kg should contain 19 triples")

        wr2 = WebResource(
            "https://covidontheweb.inria.fr/sparql?query=define%20sql%3Adescribe-mode%20%22CBD%22%20%20DESCRIBE%20%3Chttp%3A%2F%2Fns.inria.fr%2Fcovid19%2Fcovidontheweb-1-2%3E&output=text%2Fturtle"
        )
        kg2 = wr2.get_rdf()
        print(kg2.serialize(format="turtle"))

    def test_sparql_void(self):
        wr = WebResource("http://caligraph.org/.well-known/void")
        kg = wr.get_rdf()
        self.assertEquals(len(kg), 19, "the kg should contain 19 triples")

    def test_sparql_endpoint(self):
        wr = WebResource("https://www.bgee.org/sparql/")
        kg = wr.get_rdf()
        self.assertEquals(len(kg), 14, "the kg should contain 14 triples")

    def test_bfo_remote_file(self):
        wr = WebResource(
            "https://raw.githubusercontent.com/BFO-ontology/BFO/master/bfo.owl"
        )
        kg = wr.get_rdf()
        self.assertEquals(len(kg), 563, "the kg should contain 563 triples")

    def test_covid_on_the_web_remote_file(self):
        wr = WebResource(
            # "https://raw.githubusercontent.com/Wimmics/CovidOnTheWeb/master/dataset/covidontheweb-metadata-dataset.ttl"
            "https://raw.githubusercontent.com/Wimmics/CovidOnTheWeb/master/dataset/covidontheweb-definitions.ttl"
        )
        kg = wr.get_rdf()
        self.assertEquals(len(kg), 20, "the kg should contain 20 triples")
