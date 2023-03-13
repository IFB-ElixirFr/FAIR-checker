import unittest
from rdflib import ConjunctiveGraph, Namespace, Dataset
from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.WebResource import WebResource
import logging
import time
from rdflib import Graph
import requests
import extruct
import json

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
        self.assertGreaterEqual(len(bwa.get_rdf()), 121)

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
        self.assertEqual(len(dataverse.get_rdf()), 0)

    def test_workflowhub(self):
        wf = WebResource("https://workflowhub.eu/workflows/263")
        logging.info(f"{len(wf.get_rdf())} loaded RDF triples")
        print(wf.get_url())
        print(f"{len(wf.get_rdf())} loaded RDF triples")
        # print(wf.get_html_selenium())
        # print(wf.get_html_requests())
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
        self.assertEqual(35, len(fc.get_rdf()))

    def test_dataverse_jsonld(self):
        # inrae_dataverse_jsonld = WebResource("https://entrepot.recherche.data.gouv.fr/api/datasets/export?exporter=schema.org&persistentId=doi%3A10.57745/EFVOW5")
        # logging.info(f"{len(inrae_dataverse_jsonld.get_rdf())} loaded RDF triples")

        harvard_dataverse_jsonld = WebResource(
            "https://dataverse.harvard.edu/api/datasets/export?exporter=schema.org&persistentId=doi%3A10.7910/DVN/ISBMO4"
        )
        logging.info(f"{len(harvard_dataverse_jsonld.get_rdf())} loaded RDF triples")
        self.assertEqual(60, len(harvard_dataverse_jsonld.get_rdf()))

    def test_dataverse_html(self):

        harvard_dataverse_html = WebResource(
            "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ISBMO4"
        )
        logging.info(f"{len(harvard_dataverse_html.get_rdf())} loaded RDF triples")
        self.assertEqual(60, len(harvard_dataverse_html.get_rdf()))

    def test_dataverse_inrae_html(self):
        inrae_dataverse_html = WebResource(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        logging.info(f"{len(inrae_dataverse_html.get_rdf())} loaded RDF triples")
        self.assertEqual(0, len(inrae_dataverse_html.get_rdf()))

    def test_turtle(self):
        turtle_WR = WebResource("https://www.w3.org/TR/turtle/examples/example1.ttl")
        logging.info(f"{len(turtle_WR.get_rdf())} loaded RDF triples")
        # self.assertEqual(60, len(turtle_WR.get_rdf()))

    def test_n3(self):
        n3_WR = WebResource("https://www.w3.org/2002/11/rddl/ex1.n3")
        logging.info(f"{len(n3_WR.get_rdf())} loaded RDF triples")
        # self.assertEqual(60, len(n3_WR.get_rdf()))

    def test_rdfxml(self):
        rdfxml_WR = WebResource("https://www.w3.org/2002/11/rddl/ex1.xml")
        logging.info(f"{len(rdfxml_WR.get_rdf())} loaded RDF triples")
        # self.assertEqual(60, len(rdfxml_WR.get_rdf()))

    def test_pangaea(self):
        pangaea_WR = WebResource("https://doi.pangaea.de/10.1594/PANGAEA.932827")
        # logging.info(f"{len(pangaea_WR.get_rdf())} loaded RDF triples")
        self.assertEqual(246, len(pangaea_WR.get_rdf()))

    def test_uniprot(self):
        uniprot_WR = WebResource("https://www.uniprot.org/uniprotkb/P05067/entry")
        logging.info(f"{len(uniprot_WR.get_rdf())} loaded RDF triples")
        self.assertEqual(9, len(uniprot_WR.get_rdf()))

    def test_uniprot_rest(self):
        uniprot_rest_WR = WebResource("https://rest.uniprot.org/uniprotkb/P05067.rdf")
        logging.info(f"{len(uniprot_rest_WR.get_rdf())} loaded RDF triples")
        self.assertEqual(19791, len(uniprot_rest_WR.get_rdf()))

    def test_named_graph(self):

        RDFLib = Namespace("https://rdflib.github.io/")

        # turtle
        url_turtle = "https://www.w3.org/TR/turtle/examples/example1.ttl"
        response = requests.get(url_turtle)
        content_turtle = response.text
        g_turtle = ConjunctiveGraph(identifier="http://webresource/turtle")

        g_turtle.parse(data=content_turtle, format="turtle")
        g_turtle.bind("wr", Namespace("http://webresource/"))

        # n3
        url_n3 = "https://www.w3.org/2002/11/rddl/ex1.n3"
        response = requests.get(url_n3)
        content_n3 = response.text
        g_n3 = ConjunctiveGraph(identifier="http://webresource/links")

        g_n3.parse(data=content_n3, format="n3")
        g_n3.bind("wr", Namespace("http://webresource/"))

        ds = Dataset()
        ds.add_graph(g_turtle)
        ds.add_graph(g_n3)

        # g_all = g_turtle + g_n3

        # print(ds.serialize(format="trig"))
        # print(g_all.serialize(format="trig"))
        print(len(ds))
        for c in ds.graphs():
            print(len(c))
        print(len(g_turtle))
        print(len(g_n3))
        # print(len(g_all))

    def test_named_graph_pangaea(self):

        # jsonld
        url_jsonld = (
            "https://doi.pangaea.de/10.1594/PANGAEA.932827?format=metadata_jsonld"
        )
        wr_pangaea = WebResource(url_jsonld)
        content_jsonld = wr_pangaea.get_kg_auto().serialize(format="json-ld")
        g_jsonld = ConjunctiveGraph(identifier="http://webresource/jsonld")
        g_jsonld.parse(data=content_jsonld, format="json-ld", publicID=url_jsonld)
        g_jsonld.bind("wr", Namespace("http://webresource/"))

        # html
        url_html = "https://doi.pangaea.de/10.1594/PANGAEA.932827"
        wr_pangaea_html = WebResource(url_html)
        content_html = wr_pangaea_html.get_kg_html().serialize(format="json-ld")

        g_html = ConjunctiveGraph(identifier="http://webresource/html")
        g_html.parse(data=content_html, format="json-ld", publicID=url_html)
        g_html.bind("wr", Namespace("http://webresource/"))

        ds = Dataset()
        ds.add_graph(g_jsonld)
        ds.add_graph(g_html)

        # g_all = g_turtle + g_n3

        # print(ds.serialize(format="trig"))
        # print(g_all.serialize(format="trig"))

        for c in ds.graphs():
            print(len(c))
            print(c)

        print(len(g_jsonld))
        print(len(g_html))

    def test_wr_named_graph(self):
        url_html = "https://doi.pangaea.de/10.1594/PANGAEA.932827"
        wr_pangaea = WebResource(url_html)
        for c in wr_pangaea.get_wr_kg_dataset().graphs():
            print(c.identifier)
            print(len(c))

        print(wr_pangaea.get_wr_kg_dataset().serialize(format="trig"))

    def test_biotools_named_kg(self):
        bwa = WebResource("http://bio.tools/bwa")
        for kg in bwa.get_wr_kg_dataset().graphs():
            print(len(kg))
        # logging.info(f"{len(bwa.get_wr_kg_dataset())} loaded RDF triples")
        # self.assertGreaterEqual(len(bwa.get_rdf()), 121)

    # def test_define_var(self):
    #     url_html = "https://doi.pangaea.de/10.1594/PANGAEA.932827"
    #     wr_pangaea = WebResource(url_html)
    #     # wr_pangaea.init_kgs()

    #     # print(wr_pangaea.get_wr_dataset().serialize(format="trig"))

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
