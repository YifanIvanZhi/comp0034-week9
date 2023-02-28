from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Iris app folder
PROJECT_ROOT = Path(__file__).parent

# Create a global SQLAlchemy object
db = SQLAlchemy()


def create_app(config_object):
    """Create and configure the Flask app

    Args:
    config_object: configuration class (see config.py)

    Returns:
    Configured Flask app

    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Bind the Flask-SQLAlchemy instance to the Flask app
    db.init_app(app)

    # Include the routes from routes.py
    with app.app_context():
        from . import routes

        # Create the tables in the database if they do not already exist
        from .models import Iris

        db.create_all()

    return app
