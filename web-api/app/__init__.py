from flask import Flask

from .data import bp as data_bp
from .user import bp as user_bp
from .hello import bp as hello_bp
from .html2json import bp as html2json_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(data_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(html2json_bp)

    return app
