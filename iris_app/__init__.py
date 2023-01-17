from flask import Flask


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "saULPgD9XU8vzLVk7kyLBw"

    # Include the routes from routes.py
    with app.app_context():
        from . import routes

    return app
