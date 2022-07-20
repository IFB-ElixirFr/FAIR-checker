from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config(object):
    # You have to config your apikey for bioportal in a separate .env file that must not be in git
    # e.g. BIOPORTAL_APIKEY='xxxxxx-xxxxx-xxxx-xxxx-xxxxxxxx'
    BIOPORTAL_APIKEY = environ.get("BIOPORTAL_APIKEY")
    DEBUG = False
    TESTING = False
    SERVER_NAME = "0.0.0.0:5000"
    # Flask-Caching related configs
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60  # timer in seconds
    CACHE_CONTROLLED_VOCAB = 168  # timer in hours


class ProductionConfig(Config):
    SERVER_IP = "https://fair-checker.france-bioinformatique.fr"


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_IP = "http://0.0.0.0:5000"
    CACHE_DEFAULT_TIMEOUT = 30  # timer in seconds
    CACHE_CONTROLLED_VOCAB = 24  # timer in hours


class TestingConfig(Config):
    TESTING = True
