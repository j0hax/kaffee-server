class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    DATABASE = "coffee.db"


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
