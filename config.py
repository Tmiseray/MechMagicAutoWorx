from PRIVATE import *


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{MYPASSWORD}@localhost/{MYDB}'
    DEBUG = True


class TestingConfig:
    pass


class ProductionConfig:
    pass