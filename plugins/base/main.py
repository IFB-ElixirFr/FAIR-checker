## Plugin Abstract class
## 
## Every plugin created for Fair Checker should be a direct implementation of this abstract class
## to be considered a valid and usable plugin for the Fair Checker application

from abc import ABC, abstractmethod

class Plugin(ABC):

    ## Define the required fieds to add in the Plugin implementation class
    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, "VERSION"):
            raise TypeError(f"{cls.__name__} must define a 'VERSION' in your Plugin implementation class")
        if not hasattr(cls, "ID"):
            raise TypeError(f"{cls.__name__} must define a 'ID' in your Plugin implementation class")


    @property
    def getVersion(self):
        return self.__class__.VERSION

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def read_json(self, filePath):
        with open(filePath, 'r') as file:
            data = json.load(file)
        return data
    
    @abstractmethod
    def to_dict(self):
        pass


## Example of a plugin implementation
## 
## Create a Fair-Checker plugin that implements the basic abstract plugin 
## used as the base of every Fair-Checker plugins

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import json

class BasePlugin(Plugin):

    VERSION = "v0.0.1"
    ID = "base_plugin"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.datasets = self.read_json('plugins/base/datasets.json')
    
    def to_dict(self):
        return {
            "version": self.VERSION,
            "id": self.ID,
            "name": self.name,
            "description": self.description,
            "datasets": self.datasets
        }