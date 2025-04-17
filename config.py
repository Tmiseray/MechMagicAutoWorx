from PRIVATE import *


class Config:
    OPENAPI_AUTOBUNDLE = False


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{MYPASSWORD}@localhost/{MYDB}'
    DEBUG = True
    OPENAPI_AUTOBUNDLE = True


class TestingConfig:
    pass


class ProductionConfig:
    pass