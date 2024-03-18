from flask import Flask

from .data import bp as data_bp
from .user import bp as user_bp
from .discipline import bp as discipline_bp
from .error2json import bp as error2json_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(data_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(discipline_bp)
    app.register_blueprint(error2json_bp)

    return app
