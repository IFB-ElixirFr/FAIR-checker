import unittest
from webbrowser import get
import requests
from rdflib import ConjunctiveGraph
from metrics.Evaluation import Result
from metrics.FAIRMetricsFactory import FAIRMetricsFactory, Implem
from metrics.WebResource import WebResource
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class WebResourceTestCase(unittest.TestCase):
    @classmethod
    def tearDownModule(cls) -> None:
        super().tearDownModule()
        browser = WebResource.WEB_BROWSER_HEADLESS
        browser.quit()

    def test_biotools(self):
        bwa = WebResource("http://bio.tools/bwa")
        logging.info(f"{len(bwa.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(bwa.get_rdf()), 124)

    def test_dataverse(self):
        dataverse = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        logging.info(f"{len(dataverse.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(dataverse.get_rdf()), 9)

    def test_workflowhub(self):
        bwa = WebResource("https://workflowhub.eu/workflows/263")
        logging.info(f"{len(bwa.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(bwa.get_rdf()), 28)
        turtle = bwa.get_rdf().serialize(format="turtle")
        self.assertTrue("sc:ComputationalWorkflow" in turtle)

    # @unittest.skip("Using local hard path, should not be used in CI")
    def test_EDAM(self):
        EDAM_KG = ConjunctiveGraph()
        # EDAM_KG.parse("https://edamontology.org/EDAM.owl")
        EDAM_KG.parse("/Users/gaignard-a/Documents/Dev/edamverify/src/EDAM.owl")
        # print(f"Loaded {len(EDAM_KG)} triples.")
        edam = WebResource(
            "file:///Users/gaignard-a/Documents/Dev/edamverify/src/EDAM.owl",
            rdf_graph=EDAM_KG,
        )
        print(len(edam.get_rdf()))
        self.assertGreater(len(edam.get_rdf()), 36000)

        web_res = edam
        metrics_collection = []
        metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_F2B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
        metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

        row = {"ID": web_res.get_url()}
        row_time = {"ID": web_res.get_url()}
        for m in metrics_collection:
            ts1 = time.time()
            e = m.evaluate()
            duration = round((time.time() - ts1), 2)
            if e is not None:
                row[m.get_principle_tag()] = e.get_score()
                row_time[m.get_principle_tag()] = duration

        print(row)

    @unittest.skip("The test wont work without a fix")
    def test_fairchecker(self):
        fc = WebResource("https://fair-checker.france-bioinformatique.fr/")
        logging.info(f"{len(fc.get_rdf())} loaded RDF triples")

    def get_available_content(self, url):
        head = requests.head(url)
        print(head.status_code)
        if "Content-Type" in head.headers.keys():
            print("Content-Type: " + head.headers["Content-Type"])
        if "Accept" in head.headers.keys():
            print("Accept: " + head.headers["Content-Type"])
        if "alternates" in head.headers.keys():
            print("alternates: " + head.headers["alternates"])
        if "location" in head.headers.keys():
            print("location: " + head.headers["location"])

    def test_content_neg(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location
        # https://www.dbpedia.org/resources/linked-data/

        u1 = "http://ontology.inrae.fr/ppdo/page/ontology"
        # head = requests.head(u1)
        # print(head.status_code)
        # self.assertEquals(head.status_code, 200)
        # print(head.headers["Content-Type"])
        # self.assertIn("text/html", head.headers["Content-Type"])

        u2 = "http://ontology.inrae.fr/ppdo/data/ontology?output=ttl"
        # head = requests.head(u2)
        # print(head.status_code)
        # self.assertEquals(head.status_code, 200)
        # print(head.headers["Content-Type"])
        # self.assertIn("text/rdf+n3", head.headers["Content-Type"])

        u3 = "https://www.data.gouv.fr/fr/datasets/r/620f7c74-a7f2-4358-895f-7651d4a0cad5"
        # head = requests.head(u3)
        # print(head.status_code)
        # self.assertEquals(head.status_code, 302)
        # print(head.headers["Content-Type"])
        # print(head.headers)
        # if head.headers["location"]:
        #     u4 = head.headers["location"]
        #     head = requests.head(u4)
        #     print(head.status_code)
        #     self.assertEquals(head.status_code, 200)
        #     print(head.headers["Content-Type"])
        #     self.assertIn("application/zip", head.headers["Content-Type"])

        u5 = "http://ontology.inrae.fr/ppdo/data/ontology?output=ttl"
        # head = requests.head(u5)
        # print(head.status_code)
        # self.assertEquals(head.status_code, 200)
        # print(head.headers["Content-Type"])
        # self.assertIn("text/rdf+n3", head.headers["Content-Type"])

        u6 = "https://www.wikidata.org/wiki/Q71533"
        u7 = "http://www.wikidata.org/entity/Q71533"
        u8 = "http://dbpedia.org/resource/Leipzig"

        self.get_available_content(u1)
        self.get_available_content(u2)
        self.get_available_content(u3)
        # self.get_available_content(u4)
        self.get_available_content(u5)
        self.get_available_content(u6)
        self.get_available_content(u7)
        self.get_available_content(u8)


if __name__ == "__main__":
    unittest.main()
