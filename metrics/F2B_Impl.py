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

    def __init__(self, web_resource):
        super().__init__(web_resource)
        self.name = "F2.B"
        self.implem = "F2.B"
        self.desc = ""

    def weak_evaluate(self) -> bool:
        """
        at least one used ontology classe or property known in major ontology registries (OLS, BioPortal, LOV)
        """
        kg = self.get_web_resource().get_rdf()

        qres = kg.query(self.query_classes)
        for row in qres:
            logging.debug(f'evaluating class {row["class"]}')
            if ask_OLS(row["class"]):
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                return True
            elif ask_LOV(row["class"]):
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                return True
            elif ask_BioPortal(row["class"]):
                logging.debug(f"known in BioPortal")
                return True

        qres = kg.query(self.query_properties)
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if ask_OLS(row["prop"]):
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                return True
            elif ask_LOV(row["prop"]):
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                return True
            elif ask_BioPortal(row["prop"]):
                logging.debug(f"known in BioPortal")
                return True
        return False

    def strong_evaluate(self) -> bool:
        """
        all used ontology classes and properties  known in major ontology registries (OLS, BioPortal, LOV)
        """
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
                return False

        qres = kg.query(self.query_properties)
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if not (
                ask_OLS(row["prop"])
                or ask_LOV(row["prop"])
                or ask_BioPortal(row["prop"], type="property")
            ):
                logging.debug(f"{row['prop']} not known in OLS, or LOV, or BioPortal ")
                return False

        logging.info(
            "All classes and properties are known in major ontology registries"
        )
        return True
