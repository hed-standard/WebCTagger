from flask import Flask
from flask_cors import CORS
from board import pages
def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

    app.register_blueprint(pages.bp)
    return app