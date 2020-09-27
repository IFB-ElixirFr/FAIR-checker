class Config(object):
    DEBUG = False
    TESTING = False
    SERVER_NAME = "0.0.0.0:5000"


class ProductionConfig(Config):
    SERVER_IP = "https://134.158.247.212"


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_IP = "http://127.0.0.1:5000"


class TestingConfig(Config):
    TESTING = True
