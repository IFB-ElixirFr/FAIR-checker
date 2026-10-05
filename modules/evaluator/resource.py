
## ResourceExample
##
## This class is the structure for the Resource examples that are proposed 
## to the user as reference resource to check or inspect with the Fair-Checker
## application. The content of each ResourceExample is defined in the plugins
## Each plugins has a list of specific ResourceExamples.
##
class ResourceExample:

    def __init__(self, name, url):
        self.name = name
        self.url = url

    @classmethod
    def from_plugin_file_data(cls, example_resource):
        name = example_resource['name']
        url = example_resource['url']

        return cls(name, url)