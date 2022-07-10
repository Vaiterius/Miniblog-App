"""Initialize Flask application and SQLite database with configurations"""
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment

db = SQLAlchemy()
session = Session()
migrate = Migrate()
moment = Moment()

fc = {
    "min_username_length": 3,
    "max_username_length": 32,

    "min_pass_length": 8,

    "min_name_length": 2,
    "max_name_length": 50,

    "max_bio_length": 140,

    "max_title_length": 100,
    "max_desc_length": 200,
    "max_content_length": 10000,

    "max_comment_length": 1000,
}


def create_app():
    """Create Flask application"""
    # Initialize flask app and database model.
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.ProdConfig")
    app.url_map.strict_slashes = False

    session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    # Configuring logging for Heroku
    if not app.debug and not app.testing:
        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler("logs/bruhlog.log",
                max_bytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info("Bruhlog startup")

    with app.app_context():
        # Import parts of our application.
        from .contexts import contexts_bp
        from .main.routes import main_bp
        from .auth.routes import auth_bp
        from .errors.handlers import errors_bp

        # Register blueprints.
        app.register_blueprint(contexts_bp)           
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(errors_bp)

        return app

