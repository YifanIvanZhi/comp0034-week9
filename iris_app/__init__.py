from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Iris app folder
PROJECT_ROOT = Path(__file__).parent

# Create a global SQLAlchemy object
db = SQLAlchemy()


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "saULPgD9XU8vzLVk7kyLBw"
    # configure the SQLite database location
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(
        PROJECT_ROOT.joinpath("data", "iris.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    # Bind the Flask-SQLAlchemy instance to the Flask app
    db.init_app(app)

    # Include the routes from routes.py
    with app.app_context():
        from . import routes

        # Create the tables in the database if they do not already exist
        from .models import Iris

        db.create_all()

    return app
