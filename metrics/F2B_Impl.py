import logging

from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics
from metrics.util import ask_BioPortal, ask_OLS, ask_LOV
from metrics.recommendation import json_rec


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
        self.desc = """
            Weak: FAIR-Checker verifies that at least one used ontology class or property are known in major ontology registries (OLS, BioPortal, LOV)<br><br>
            Strong: FAIR-Checker verifies that all used ontology classes or properties are known in major ontology registries (OLS, BioPortal, LOV)
        """

    def weak_evaluate(self, eval=None):
        """
        at least one used ontology classe or property known in major ontology registries (OLS, BioPortal, LOV)
        """
        if not eval:
            eval = self.get_evaluation()
            eval.set_implem(self.implem)
            eval.set_metrics(self.principle_tag)
        kg = self.get_web_resource().get_rdf()

        if len(kg) == 0:
            eval.set_score(0)
            return eval

        eval.log_info("Weak evaluation:")
        eval.log_info(
            "Checking if at least one class used in RDF is known in OLS, LOV, or BioPortal"
        )
        qres = kg.query(self.query_classes)
        for row in qres:
            logging.debug(f'evaluating class {row["class"]}')
            if ask_OLS(row["class"]):
                eval.log_info(f"{row['class']} known in Ontology Lookup Service (OLS)")
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                eval.set_score(1)
                return eval
            elif ask_LOV(row["class"]):
                eval.log_info(f"{row['class']} known in Linked Open Vocabularies (LOV)")
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                eval.set_score(1)
                return eval
            elif ask_BioPortal(row["class"], type="class"):
                eval.log_info(f"{row['class']} known in BioPortal")
                logging.debug(f"known in BioPortal")
                eval.set_score(1)
                return eval

        eval.log_info(
            "Checking if at least one property used in RDF is known in OLS, LOV, or BioPortal"
        )
        qres = kg.query(self.query_properties)
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if ask_OLS(row["prop"]):
                eval.log_info(f"{row['prop']} known in Ontology Lookup Service (OLS)")
                logging.debug(f"known in Ontology Lookup Service (OLS)")
                eval.set_score(1)
                return eval
            elif ask_LOV(row["prop"]):
                eval.log_info(f"{row['prop']} known in Linked Open Vocabularies (LOV)")
                logging.debug(f"known in Linked Open Vocabularies (LOV)")
                eval.set_score(1)
                return eval
            elif ask_BioPortal(row["prop"], type="property"):
                eval.log_info(f"{row['prop']} known in BioPortal")
                eval.set_score(1)
                return eval

        eval.log_info(
            "No classes nor properties were found in one of the ontology registries"
        )
        eval.set_recommendations(json_rec["F2B"]["reco3"])
        eval.set_score(0)
        return eval

    def strong_evaluate(self, eval=None):
        """
        all used ontology classes and properties  known in major ontology registries (OLS, BioPortal, LOV)
        """
        if not eval:
            eval = self.get_evaluation()
            eval.set_implem(self.implem)
            eval.set_metrics(self.principle_tag)
        kg = self.get_web_resource().get_rdf()

        if len(kg) == 0:
            eval.log_info(
                "No RDF found in the web page, can't evaluate if classes or properties are known in OLS, LOV, or BioPortal"
            )
            eval.set_recommendations(json_rec["F2A"]["reco1"])
            eval.set_score(0)
            return eval

        eval.log_info("Strong evaluation:")

        eval.log_info(
            "Checking if all classes used in RDF are known in OLS, LOV, or BioPortal"
        )

        qres = kg.query(self.query_classes)
        class_not_in_registries = False
        for row in qres:
            logging.debug(f'evaluating class {row["class"]}')
            if not (
                ask_OLS(row["class"])
                or ask_LOV(row["class"])
                or ask_BioPortal(row["class"], type="class")
            ):
                logging.debug(f"{row['class']} not known in OLS, LOV, or BioPortal")
                eval.log_warning(
                    f"{row['class']} class not known in OLS, LOV, or BioPortal"
                )

                class_not_in_registries = True
                # return eval

        # True if one of the classes is not in OLS, LOV or BioPortal
        if class_not_in_registries:
            eval.set_recommendations(json_rec["F2B"]["reco1"])
        else:
            eval.log_info("All classes found in those ontology registries")

        eval.log_info(
            "Checking if all properties used in RDF are known in OLS, LOV, or BioPortal"
        )
        qres = kg.query(self.query_properties)
        property_not_in_registries = False
        for row in qres:
            logging.debug(f'evaluating property {row["prop"]}')
            if not (
                ask_OLS(row["prop"])
                or ask_LOV(row["prop"])
                or ask_BioPortal(row["prop"], type="property")
            ):
                logging.debug(f"{row['prop']} not known in OLS, or LOV, or BioPortal ")
                eval.log_warning(
                    f"{row['prop']} property not known in OLS, LOV, or BioPortal"
                )

                property_not_in_registries = True
                # return eval

        # True if one of the properties is not in OLS, LOV or BioPortal
        if property_not_in_registries:
            eval.set_recommendations(json_rec["F2B"]["reco2"])
        else:
            eval.log_info("All properties found in those ontology registries")

        # if True, go to weak evaluation
        if class_not_in_registries or property_not_in_registries:
            eval.set_score(0)
            return eval

        eval.log_info(
            "All classes and properties are known in major ontology registries"
        )
        logging.info(
            "All classes and properties are known in major ontology registries"
        )
        eval.set_score(2)
        return eval
