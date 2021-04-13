import unittest

from profiles.bioschemas_shape_gen import  gen_SHACL_from_profile
from profiles.bioschemas_shape_gen import  gen_SHACL_from_target_class
from profiles.bioschemas_shape_gen import  validate_shape_from_RDF
from profiles.bioschemas_shape_gen import  validate_any_from_RDF
from profiles.bioschemas_shape_gen import  validate_any_from_microdata
from profiles.bioschemas_shape_gen import  validate_shape_from_microdata

class GenSHACLTestCase(unittest.TestCase):

    def test_validate_shape_tool(self):
        classes = ['sc:SoftwareApplication']
        minimal_software_properties = ['sc:name', 'sc:description', 'sc:url']
        recommended_software_properties = ['sc:additionalType', 'sc:applicationCategory',
                                           'sc:applicationSubCategory', 'sc:author' 'sc:license',
                                           'sc:citation', 'sc:featureList', 'sc:softwareVersion']

        shape = gen_SHACL_from_profile("toolShape", target_classes=classes, min_props=minimal_software_properties, rec_props=recommended_software_properties)

        validate_shape_from_RDF(input_uri='https://bio.tools/api/jaspar?format=jsonld', rdf_syntax='json-ld', shacl_shape=shape)

    def test_validate_shape_dataset(self):
        classes = ['sc:Dataset']
        minimal_dataset_properties = ['sc:name', 'sc:description', 'sc:identifier', 'sc:keywords', 'sc:url']
        recommended_dataset_properties = ['sc:license', 'sc:creator', 'sc:citation']

        shape = gen_SHACL_from_profile("datasetShape", target_classes=classes, min_props=minimal_dataset_properties, rec_props=recommended_dataset_properties)
        validate_shape_from_microdata(input_uri='https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ', shacl_shape=shape)

    def test_generate_right_shape(self):
        target_class = 'sc:SoftwareApplication'
        shape = gen_SHACL_from_target_class(target_class=target_class)
        validate_shape_from_RDF(input_uri='https://bio.tools/api/jaspar?format=jsonld', rdf_syntax='json-ld', shacl_shape=shape)

    def test_any_resource(self):
        # todo assertions on error count for each test
        validate_any_from_RDF(input_url='https://bio.tools/api/jaspar?format=jsonld', rdf_syntax='json-ld')
        validate_any_from_microdata(input_url='https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/PL3HWQ')
        # todo assertions : no errors
        validate_any_from_microdata(input_url="https://doi.pangaea.de/10.1594/PANGAEA.914331")
        res = validate_any_from_microdata(input_url="https://search.datacite.org/works/10.7892/boris.108387")
        print(res)

if __name__ == '__main__':
    unittest.main()
