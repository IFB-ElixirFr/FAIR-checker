import unittest
import json
import requests
from rdflib import ConjunctiveGraph, Graph
from metrics.util import ask_OLS, ask_LOV, ask_BioPortal


class MyTestCase(unittest.TestCase):


    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        print("STARTING all tests")

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        print("ENDING all tests")

    def test_OLS(self):
        uri1 = "https://bio.tools/bwa"
        self.assertFalse(ask_OLS(uri1))
        uri2 = "http://schema.org/Organization"
        self.assertFalse(ask_OLS(uri2))
        uri3 = "http://www.ebi.ac.uk/efo/EFO_0000001"
        self.assertTrue(ask_OLS(uri3))

    def test_LOV(self):
        uri1 = "https://bio.tools/bwa"
        self.assertFalse(ask_LOV(uri1))
        uri2 = "http://schema.org/Organization"
        self.assertTrue(ask_LOV(uri2))
        uri3 = "http://www.ebi.ac.uk/efo/EFO_0000001"
        self.assertFalse(ask_LOV(uri3))



if __name__ == '__main__':
    unittest.main()
