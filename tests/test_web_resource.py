import unittest
from rdflib import ConjunctiveGraph
from metrics.FAIRMetricsFactory import FAIRMetricsFactory
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

    def test_datacite(self):
        datacite = WebResource("https://search.datacite.org/works/10.7892/boris.108387")
        logging.info(f"{len(datacite.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(datacite.get_rdf()), 45)

    # @unittest.skip(
    #     "This dataverse seems to not expose any schema.org annotations (checked with the schema.org validator)"
    # )
    def test_dataverse(self):
        dataverse = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        logging.info(f"{len(dataverse.get_rdf())} loaded RDF triples")
        self.assertEqual(len(dataverse.get_rdf()), 0)
        print()

    def test_workflowhub(self):
        wf = WebResource("https://workflowhub.eu/workflows/263")
        logging.info(f"{len(wf.get_rdf())} loaded RDF triples")
        print(wf.get_url)
        print(f"{len(wf.get_rdf())} loaded RDF triples")
        print(wf.get_html_selenium())
        print(wf.get_html_requests())
        self.assertGreaterEqual(len(wf.get_rdf()), 28)
        turtle = wf.get_rdf().serialize(format="turtle")
        self.assertTrue("sc:ComputationalWorkflow" in turtle)

    def test_workflowhub_relative_URIs(self):
        wf = WebResource("https://workflowhub.eu/workflows/118")
        turtle = wf.get_rdf().serialize(format="nt")
        self.assertTrue("file://" not in turtle)

    @unittest.skip("Using local hard path, should not be used in CI")
    def test_EDAM(self):
        EDAM_KG = ConjunctiveGraph()
        # EDAM_KG.parse("https://edamontology.org/EDAM.owl")
        EDAM_KG.parse("/Users/gaignard-a/Documents/Dev/edamverify/src/EDAM.owl")
        print(f"Loaded {len(EDAM_KG)} triples.")
        edam = WebResource(
            "file:///Users/gaignard-a/Documents/Dev/edamverify/src/EDAM.owl",
            rdf_graph=EDAM_KG,
        )
        print(len(edam.get_rdf()))
        self.assertGreater(len(edam.get_rdf()), 36000)

        web_res = edam
        metrics_collection = []
        metrics_collection.append(FAIRMetricsFactory.get_2(web_res))
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

    # @unittest.skip("The test wont work without a fix")
    def test_fairchecker(self):
        fc = WebResource("https://fair-checker.france-bioinformatique.fr/")
        logging.info(f"{len(fc.get_rdf())} loaded RDF triples")

    def test_dataverse_jsonld(self):
        # inrae_dataverse_jsonld = WebResource("https://entrepot.recherche.data.gouv.fr/api/datasets/export?exporter=schema.org&persistentId=doi%3A10.57745/EFVOW5")
        # logging.info(f"{len(inrae_dataverse_jsonld.get_rdf())} loaded RDF triples")

        harvard_dataverse_jsonld = WebResource(
            "https://dataverse.harvard.edu/api/datasets/export?exporter=schema.org&persistentId=doi%3A10.7910/DVN/ISBMO4"
        )
        logging.info(f"{len(harvard_dataverse_jsonld.get_rdf())} loaded RDF triples")

    def test_dataverse_html(self):

        harvard_dataverse_html = WebResource(
            "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ISBMO4"
        )
        logging.info(f"{len(harvard_dataverse_html.get_rdf())} loaded RDF triples")

    def test_turtle(self):
        turtle_WR = WebResource("https://www.w3.org/TR/turtle/examples/example1.ttl")
        logging.info(f"{len(turtle_WR.get_rdf())} loaded RDF triples")

    def test_n3(self):
        n3_WR = WebResource("https://www.w3.org/2002/11/rddl/ex1.n3")
        logging.info(f"{len(n3_WR.get_rdf())} loaded RDF triples")

    def test_rdfxml(self):
        rdfxml_WR = WebResource("https://www.w3.org/2002/11/rddl/ex1.xml")
        logging.info(f"{len(rdfxml_WR.get_rdf())} loaded RDF triples")

    def test_pangaea(self):
        pangaea_WR = WebResource("https://doi.pangaea.de/10.1594/PANGAEA.932827")
        logging.info(f"{len(pangaea_WR.get_rdf())} loaded RDF triples")

    def test_uniprot(self):
        uniprot_WR = WebResource("https://www.uniprot.org/uniprotkb/P05067/entry")
        logging.info(f"{len(uniprot_WR.get_rdf())} loaded RDF triples")


if __name__ == "__main__":
    unittest.main()
