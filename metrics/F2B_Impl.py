import logging

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.util import ask_BioPortal, ask_OLS, ask_LOV


class F2B_Impl(AbstractFAIRMetrics):

    query_classes = """
            SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
        """
    query_properties = """
            SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
        """

    """
    GOAL :

    """

    def __init__(self, web_resource=None):
        super().__init__(web_resource)
        self.name = "Shared vocabularies for metadata"
        self.id = "4"
        self.principle = "https://w3id.org/fair/principles/terms/F2"
        self.principle_tag = "F2B"
        self.implem = "FAIR-Checker"
        self.desc = ""

    def weak_evaluate(self, eval=None):
        """
        at least one used ontology classe or property known in major ontology registries (OLS, BioPortal, LOV)
        """
        if not eval:
            eval = self.get_evaluation()
        kg = self.get_web_resource().get_rdf()

        qres = kg.query(self.query_classes)
        for row in qres:
            logging.debug(f'evaluating class {row["class"]}')
            if ask_OLS(row["class"]):
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                eval.set_score(1)
                return eval
            elif ask_LOV(row["class"]):
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                eval.set_score(1)
                return eval
            elif ask_BioPortal(row["class"], type="class"):
                logging.debug(f"known in BioPortal")
                eval.set_score(1)
                return eval

        qres = kg.query(self.query_properties)
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if ask_OLS(row["prop"]):
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                eval.set_score(1)
                return eval
            elif ask_LOV(row["prop"]):
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                eval.set_score(1)
                return eval
            elif ask_BioPortal(row["prop"], type="property"):
                logging.debug(f"known in BioPortal")
                eval.set_score(1)
                return eval
        eval.set_score(0)
        return eval

    def strong_evaluate(self, eval=None):
        """
        all used ontology classes and properties  known in major ontology registries (OLS, BioPortal, LOV)
        """
        if not eval:
            eval = self.get_evaluation()
        kg = self.get_web_resource().get_rdf()

        qres = kg.query(self.query_classes)
        for row in qres:
            logging.debug(f'evaluating class {row["class"]}')
            if not (
                ask_OLS(row["class"])
                or ask_LOV(row["class"])
                or ask_BioPortal(row["class"], type="class")
            ):
                logging.debug(f"{row['class']} not known in OLS, or LOV, or BioPortal")
                eval.set_score(0)
                return eval

        qres = kg.query(self.query_properties)
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if not (
                ask_OLS(row["prop"])
                or ask_LOV(row["prop"])
                or ask_BioPortal(row["prop"], type="property")
            ):
                logging.debug(f"{row['prop']} not known in OLS, or LOV, or BioPortal ")
                eval.set_score(0)
                return eval

        logging.info(
            "All classes and properties are known in major ontology registries"
        )
        eval.set_score(2)
        return eval
