"""Initialize Flask application and SQLite database with configurations"""
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
session = Session()
migrate = Migrate()

fc = {
    "min_username_length": 3,
    "max_username_length": 32,

    "min_pass_length": 8,

    "min_name_length": 2,
    "max_name_length": 50,
}


def create_app():
    """Create Flask application"""
    # Initialize flask app and database model.
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.DevConfig")

    session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

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

