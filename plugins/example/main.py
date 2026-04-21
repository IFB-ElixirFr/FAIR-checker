## Plugin Abstract class
## 
## Every plugin created for Fair Checker should be a direct implementation of this abstract class
## to be considered a valid and usable plugin for the Fair Checker application

from abc import ABC, abstractmethod

class Plugin(ABC):

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def read_datasets(self):
        pass


## Example of a plugin implementation
## 
## Create a Fair-Checker plugin that implements the basic abstract plugin 
## used as the base of every Fair-Checker plugins

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import json

class ExamplePlugin(Plugin):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.datasets = self.read_datasets()

    def read_datasets(self):
        with open('plugins/example/datasets.json', 'r') as file:
            data = json.load(file)
        return data

##example_plugin = Blueprint('example_plugin', __name__, template_folder='templates')
##
##@example_plugin.route('/', defaults={'page': 'index'})
##@example_plugin.route('/plugins/<page>')
##def show(page):
##    try:
##        return render_template(f'{page}.html')
##    except TemplateNotFound:
##        abort(404)