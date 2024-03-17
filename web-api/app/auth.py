import re
from hashlib import sha256
from http import HTTPStatus
from uuid import uuid4
from functools import wraps

from flask import request

from .data import data
from .user import bp as user_bp

AUTH_KEY_MIN_CHARACTERS = 32
AUTH_KEY_MAX_CHARACTERS = 256

def validate_auth_key_security(key):
    problems = []
    n = len(key)

    if n < AUTH_KEY_MIN_CHARACTERS:
        problems.append(("Minimum key length must be "
                         f"{AUTH_KEY_MIN_CHARACTERS} characters."))

    if n > AUTH_KEY_MAX_CHARACTERS:
        problems.append(("Maximum key length must be "
                         f"{AUTH_KEY_MAX_CHARACTERS} characters."))

    if re.search(r"[a-zAZ]", key) is None or re.search(r"[0-9]", key) is None:
        problems.append("Key must contain both letters and numbers.")

    return problems

def generate_auth_key():
    while True:
        key = str(uuid4().hex)
        problems = validate_auth_key_security(key)
        if len(problems) == 0:
            return key

def hash_auth_key(key):
    return sha256(key.encode("utf-8")).hexdigest()

def require_auth_key(user_to_be_accessed):
    username = None
    key = None
    path = request.path
    authorization = request.authorization
    authenticated = False

    if authorization is not None and authorization.type == "basic":
        username = authorization.username
        key = authorization.password

    if username is None and path.startswith(user_bp.url_prefix):
        username = path.removeprefix(user_bp.url_prefix).split("/", 1)[0]

    if key is None and "key" in request.args:
        key = request.args["key"]

    if key is not None and "users" in data and username in data["users"]:
        saved_hashed_key = data["users"][username]["hashed_auth_key"]
        authenticated = saved_hashed_key == hash_auth_key(key)

    if not authenticated:
        return {
            "type": "problems/unauthorized",
            "title": "Not authorized",
            "detail": "Incorrect authentication credentials"
        }, HTTPStatus.UNAUTHORIZED, {
            "WWW-Authenticate": "Basic"
        }

    if username != "root" and user_to_be_accessed != username:
        return {
            "type": "problems/forbidden_to_access_another_user",
            "title": "Forbidden to access another user"
        }, HTTPStatus.FORBIDDEN, None

    return None, None, None

def auth_key_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        problem, code, headers = require_auth_key(user)

        if problem:
            return problem, code, headers

        return func(user, *args, **kwargs)

    return wrapper
