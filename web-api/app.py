from flask import Flask, make_response, request
import json

app = Flask(__name__)

@app.route("/helloWorld", methods=['GET'])
def getHelloWorld():
    return make_response("Hello world!")