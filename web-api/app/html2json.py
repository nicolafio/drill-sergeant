"""
This module helps to translate on the fly to JSON form the default HTML problems
from Flask.

As Drill Sergeant is primarily a JSON-based web API, I'd like to give responses
in JSON format whenever possible. I haven't found a better way to instruct Flask
to give problem responses in JSON.
"""
import json

from pyquery import PyQuery as pq
from flask import make_response

def is_html_problem(response):
    status_code = response.status_code
    content_type = response.headers["Content-Type"]
    return status_code >= 400 and "text/html" in content_type

def convert_html_problem_to_json(response):
    json_response = make_response(response)

    html = response.get_data(as_text = True)
    d = pq(html)

    title = d("title").text()
    detail = d("body").text()
    title_snake_case = title.lower().replace(" ", "_")

    json_response.headers["Content-Type"] = "application/json"
    json_response.data = json.dumps({
        "type": f"problems/{title_snake_case}",
        "title": title,
        "detail": detail
    })

    return json_response
