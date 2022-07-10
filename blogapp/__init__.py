"""Initialize Flask application and SQLite database with configurations"""
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
    app.config.from_object("config.DevConfig")
    app.url_map.strict_slashes = False

    session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

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

