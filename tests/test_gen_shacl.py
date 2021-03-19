import unittest
from rdflib import ConjunctiveGraph
from jinja2 import Template
from pyshacl import validate

from metrics.R2Impl import R2Impl
from profiles.bioschemas_shape_gen import  gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import  validate_shape_from_RDF
from profiles.bioschemas_shape_gen import  validate_shape_from_microdata

class GenSHACLTestCase(unittest.TestCase):

    def test_validate_shape_tool(self):

        #classes = ['schema:Dataset']
        #minimal_dataset_properties = ['schema:name', 'schema:description', 'schema:identifier', 'schema:keywords', 'schema:url']
        #recommended_dataset_properties = ['schema:license', 'schema:creator', 'schema:citation']

        classes = ['schema:SoftwareApplication']
        minimal_software_properties = ['schema:name', 'schema:description', 'schema:url']
        recommended_software_properties = ['schema:additionalType', 'schema:applicationCategory',
                                           'schema:applicationSubCategory', 'schema:author' 'schema:license',
                                           'schema:citation', 'schema:featureList', 'schema:softwareVersion']

        shape = gen_SHACL_from_profile("toolShape", target_classes=classes, min_props=minimal_software_properties, rec_props=recommended_software_properties)

        validate_shape_from_RDF(input_uri='https://bio.tools/api/jaspar?format=jsonld', rdf_syntax='json-ld', shacl_shape=shape)

    def test_validate_shape_dataset(self):

        classes = ['schema:Dataset']
        minimal_dataset_properties = ['schema:name', 'schema:description', 'schema:identifier', 'schema:keywords', 'schema:url']
        recommended_dataset_properties = ['schema:license', 'schema:creator', 'schema:citation']

        shape = gen_SHACL_from_profile("datasetShape", target_classes=classes, min_props=minimal_dataset_properties, rec_props=recommended_dataset_properties)

        validate_shape_from_microdata(input_uri='https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ', shacl_shape=shape)




if __name__ == '__main__':
    unittest.main()
