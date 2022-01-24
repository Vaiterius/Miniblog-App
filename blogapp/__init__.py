"""Initialize Flask application and SQLite database with configurations"""
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize flask app and database model.
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ensure templates are auto-reloaded.
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem in lieu of signed cookies.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

form_constraints = {
    "min_username_length": 3,
    "max_username_length": 32,

    "min_pass_length": 8,

    "min_name_length": 2,
    "max_name_length": 50,
}

import blogapp.routes
