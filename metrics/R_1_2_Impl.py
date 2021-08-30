from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
import validators

class R_1_2_Impl(AbstractFAIRMetrics):
    """
    GOAL : retrieve embedded semantic annotations
    """

    def __init__(self, url):
        self.name = "R1.2"
        self.desc = "Metadata includes provenance. Evaluate if " " properties exist."
        self.url = url

    def get_classes(self):
        query_classes = """
            SELECT DISTINCT ?class WHERE { ?s rdf:type ?class } ORDER BY ?class
        """
        return self.rdf_jsonld.query(query_classes)

    def get_properties(self):
        query_properties = """
            SELECT DISTINCT ?prop WHERE { ?s ?prop ?o } ORDER BY ?prop
        """
        return self.rdf_jsonld.query(query_properties)

    def get_api(self):
        return self.api

    def get_html_source(self):
        return self.html_source

    def get_jsonld(self):
        return self.rdf_jsonld

    def is_valid_uri(self, uri):
        return validators.url(uri)

    def evaluate(self):
        #         eval = Evaluation()
        #         eval.set_start_time()

        #         eval.result_text = testMetric(self.api, data)

        #         # print(eval.result_text)
        #         eval.set_end_time()
        #         # evaluation_obj.result_json = json.loads(self.result_text)
        #         eval.set_score(requestResultSparql(eval.result_text, "ss:SIO_000300"))
        #         eval.set_reason(requestResultSparql(eval.result_text, "schema:comment"))
        #         # principle are URLs so we get the last element after the last /
        #         eval.set_metrics(self.principle.split("/")[-1])
        #         eval.set_target_uri(url)
        #         eval.persist()
        #         return eval
        pass

    def evaluate_prov(self):
        print("Evaluating R1.2")
        self.extract_html_requests()
        self.extract_rdf()

        query_prov = """
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX dct: <http://purl.org/dc/terms/> 
            ASK { 
                VALUES ?p {prov:tocomplete dct:tocomplete} . 
                ?s ?p ?o .
            }
        """

        res = self.rdf_jsonld.query(query_prov)
        for bool_res in res:
            return bool_res
