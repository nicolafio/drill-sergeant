from flask import Flask, make_response, request
import json

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from . import day_discipline
        return app
