from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config(object):
    # You have to config your apikey for bioportal in a separate .env file that must not be in git
    # e.g. BIOPORTAL_APIKEY='xxxxxx-xxxxx-xxxx-xxxx-xxxxxxxx'
    BIOPORTAL_APIKEY = environ.get("BIOPORTAL_APIKEY")
    GITHUB_TOKEN = environ.get("GITHUB_TOKEN")
    DEBUG = False
    TESTING = False
    # SERVER_NAME = "0.0.0.0:5000"
    # Flask-Caching related configs
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60  # timer in seconds for metrics
    CACHE_CONTROLLED_VOCAB_TIMER = (
        168  # timer in hours for Vocabularies (OLS, LOV, BioPortal)
    )
    CACHE_CONTROLLED_VOCAB_MAXSIZE = (
        20000  # Number of element stored for Vocabularies (OLS, LOV, BioPortal)
    )
    CACHE_DEFAULT_MD_TTL = 600  # in seconds
    CACHE_DEFAULT_EVAL_TTL = 600  # in seconds


# Used only when SERVER_URL is set neither in the environment nor in .env
DEFAULT_LOCAL_SERVER_URL = "http://127.0.0.1:5000"


def _server_url(default=None):
    """SERVER_URL from the environment (or .env), without trailing slash.
    None when it is set nowhere and no default is given."""
    url = environ.get("SERVER_URL") or default  # empty counts as unset
    return url.rstrip("/") if url else None


def _under(base_url, path):
    """base_url + path, or None when base_url is not set."""
    return base_url + path if base_url else None


class ProductionConfig(Config):
    SERVER_URL = environ.get("SERVER_URL")
    # EVAL_URL = "https://fair-checker.france-bioinformatique.fr/eval/"
    EVAL_URL = "https://w3id.org/fairchecker/eval/"
    # ASSESSMENT_URL = "https://fair-checker.france-bioinformatique.fr/assessment/"
    ASSESSMENT_URL = "https://w3id.org/fairchecker/assessment/"
    # Base IRI of the test descriptions referenced from the RDF test results
    TEST_URL = "https://w3id.org/fairchecker/test/"


class StagingConfig(Config):
    """Public dev instance: the W3ID URLs redirect to production, so the IRIs
    minted here must point to this server to stay resolvable."""

    # No default: app.py refuses to start in staging without SERVER_URL
    SERVER_URL = _server_url()
    EVAL_URL = _under(SERVER_URL, "/eval/")
    ASSESSMENT_URL = _under(SERVER_URL, "/assessment/")
    TEST_URL = _under(SERVER_URL, "/test/")


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_URL = _server_url(DEFAULT_LOCAL_SERVER_URL)
    EVAL_URL = SERVER_URL + "/eval/"
    ASSESSMENT_URL = SERVER_URL + "/assessment/"
    TEST_URL = SERVER_URL + "/test/"
    CACHE_DEFAULT_TIMEOUT = 30  # timer in seconds
    CACHE_CONTROLLED_VOCAB_TIMER = (
        24  # timer in hours for Vocabularies (OLS, LOV, BioPortal)
    )
    CACHE_CONTROLLED_VOCAB_MAXSIZE = (
        500  # Number of element stored for Vocabularies (OLS, LOV, BioPortal)
    )


class TestingConfig(Config):
    TESTING = True
    SERVER_URL = _server_url(DEFAULT_LOCAL_SERVER_URL)
    EVAL_URL = SERVER_URL + "/eval/"
    ASSESSMENT_URL = SERVER_URL + "/assessment/"
    TEST_URL = SERVER_URL + "/test/"
    # MONGO_HOST = "0.0.0.0"
    # MONGO_PORT = 27017
    # MONGO_DBNAME = "fair_checker"
    # MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}"
    # TESTING = True
