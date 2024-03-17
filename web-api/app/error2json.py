"""
This module helps to translate on the fly to JSON form the default HTML problems
from Flask.

As Drill Sergeant is primarily a JSON-based web API, I'd like to give responses
in JSON format whenever possible. I haven't found a better way to instruct Flask
to give problem responses in JSON.
"""
import json

from pyquery import PyQuery as pq
from flask import Blueprint

bp = Blueprint("html2json", __name__)

def _is_html_problem(response):
    status_code = response.status_code
    content_type = response.headers["Content-Type"]
    return status_code >= 400 and "text/html" in content_type

def _convert_html_problem_to_json(response):
    html = response.get_data(as_text = True)
    d = pq(html)

    title = d("title").text()
    detail = d("body").text()
    title_snake_case = title.lower().replace(" ", "_")

    response.headers["Content-Type"] = "application/json"
    response.data = json.dumps({
        "type": f"problems/{title_snake_case}",
        "title": title,
        "detail": detail
    })

    return response

@bp.after_app_request
def _after_request(response):
    if _is_html_problem(response):
        return _convert_html_problem_to_json(response)

    return response
