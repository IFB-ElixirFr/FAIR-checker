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
    CACHE_DEFAULT_TIMEOUT = 60  # timer in seconds for metrics
    CACHE_CONTROLLED_VOCAB_TIMER = (
        168  # timer in hours for Vocabularies (OLS, LOV, BioPortal)
    )
    CACHE_CONTROLLED_VOCAB_MAXSIZE = (
        20000  # Number of element stored for Vocabularies (OLS, LOV, BioPortal)
    )


class ProductionConfig(Config):
    SERVER_IP = "https://fair-checker.france-bioinformatique.fr"


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_IP = "http://0.0.0.0:5000"
    CACHE_DEFAULT_TIMEOUT = 30  # timer in seconds
    CACHE_CONTROLLED_VOCAB_TIMER = (
        24  # timer in hours for Vocabularies (OLS, LOV, BioPortal)
    )
    CACHE_CONTROLLED_VOCAB_MAXSIZE = (
        500  # Number of element stored for Vocabularies (OLS, LOV, BioPortal)
    )


class TestingConfig(Config):
    TESTING = True
    SERVER_IP = "http://0.0.0.0:5000"
    # MONGO_HOST = "0.0.0.0"
    # MONGO_PORT = 27017
    # MONGO_DBNAME = "fair_checker"
    # MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}"
    # TESTING = True
