from flask import Flask

from .user import bp as user_bp
from .hello import bp as hello_bp
from .data import save_data_if_needed
from .html2json import is_html_problem
from .html2json import convert_html_problem_to_json

def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    app.register_blueprint(hello_bp)

    @app.after_request
    def after_request(response):
        save_data_if_needed(app)

        if is_html_problem(response):
            return convert_html_problem_to_json(response)

        return response

    return app
