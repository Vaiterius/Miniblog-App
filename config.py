"""Flask configuration"""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base configuration"""
    FLASK_APP = "wsgi.py"
    # FLASK_ENV = "development"
    FLASK_ENV = "production"
    SECRET_KEY = environ.get("SECRET_KEY")
    POSTS_PER_PAGE = 8
    POSTS_PER_PAGE = 12

    S3_BUCKET = environ.get("S3_BUCKET")
    S3_BUCKET_TEMP = environ.get("S3_BUCKET_TEMP")
    S3_KEY = environ.get("S3_KEY")
    S3_SECRET = environ.get("S3_SECRET")

    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    TEMPLATES_AUTO_RELOAD = True

    LOG_TO_STDOUT = 1


class ProdConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = environ.get("PROD_DATABASE_URI", "").replace(
        "postgres://", "postgresql://") or \
        "sqlite:///" + path.join(basedir, "app.db")
    SQLALCHEMY_ECHO = False


class DevConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_ECHO = False

