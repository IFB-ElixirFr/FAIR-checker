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
        self.assertEqual(len(dataverse.get_rdf()), 234)
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

    def test_fairchecker(self):
        fc = WebResource("https://fair-checker.france-bioinformatique.fr/")
        logging.info(f"{len(fc.get_rdf())} loaded RDF triples")
        self.assertGreaterEqual(len(fc.get_rdf()), 35)

    def test_elixir(self):
        elixir = WebResource("https://www.elixir-europe.org/")
        logging.info(f"{len(elixir.get_rdf())} loaded RDF triples")

    def test_biosamples(self):
        biosamples = WebResource("https://www.ebi.ac.uk/biosamples/")
        logging.info(f"{len(biosamples.get_rdf())} loaded RDF triples")

    def test_pscan(self):
        pscan = WebResource("http://159.149.160.88/pscan/")
        logging.info(f"{len(pscan.get_rdf())} loaded RDF triples")

    def test_expasy(self):
        expasy = WebResource("https://prosite.expasy.org")
        logging.info(f"{len(expasy.get_rdf())} loaded RDF triples")

    def test_UnicodeDecodeError_resources(self):
        # Workflohub is working correctly, it is a positive control
        urls = [
            # "https://workflowhub.eu/workflows/18"
            # "https://ebisc.org/",
            "https://www.metanetx.org/",
            # "https://www.ebi.ac.uk/interpro/",
            # "https://datacatalog.elixir-luxembourg.org/",
            # "https://ippidb.pasteur.fr/",
            # "http://edgar.biocomp.unibo.it/",
            # "http://phenpath.biocomp.unibo.it/phenpath/",
            # "https://humanmine.org/",
            # "https://prosite.expasy.org",
            # "https://enzyme.expasy.org",
            # "https://hamap.expasy.org/",
            # "https://www.ebi.ac.uk/chembl/",
            # "http://www.ebi.ac.uk/Tools/hmmer/",
        ]

        for url in urls:
            wr_kg = WebResource(url).get_rdf()
            print(len(wr_kg))

    def test_schema_file_context(self):
        urls = [
            # "https://www.metanetx.org/",
            "https://bio.tools/jaspar"
        ]

        for url in urls:
            wr_kg = WebResource(url).get_rdf()
            print(len(wr_kg))


if __name__ == "__main__":
    unittest.main()
