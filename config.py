"""Flask configuration"""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base configuration"""
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    SECRET_KEY = environ.get("SECRET_KEY")

    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    TEMPLATES_AUTO_RELOAD = True


class ProdConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = environ.get("PROD_DATABASE_URI")
    SQLALCHEMY_ECHO = False


class DevConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = environ.get("DEV_DATABASE_URI")
    SQLALCHEMY_ECHO = False

