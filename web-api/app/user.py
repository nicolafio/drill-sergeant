from http import HTTPStatus
from functools import wraps

from flask import Blueprint
from flask import request

import validators

from .auth import validate_auth_key_security
from .auth import generate_auth_key
from .auth import hash_auth_key
from .auth import require_auth_key
from .auth import auth_key_required
from .data import data
from .data import raise_data_update

bp = Blueprint("user", __name__, url_prefix = "/v1/user")

def require_user_existence(user):
    if "users" not in data or user not in data["users"]:
        return {
            "type": "problems/user_not_found",
            "title": "User not found"
        }, HTTPStatus.NOT_FOUND

    return None, None

def user_existence_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        problem, code = require_user_existence(user)

        if problem:
            return problem, code

        return func(user, *args, **kwargs)

    return wrapper

def _get_user_representation(user):
    representation = dict(data["users"][user])
    del representation["hashed_auth_key"]
    return representation


def _is_external_url(url):
    return validators.url(url, public = True)

@bp.route("/<user>", methods = ["GET"])
@auth_key_required
@user_existence_required
def get_user(user):
    return _get_user_representation(user)

@bp.route("/<user>", methods = ["PUT", "PATCH"])
def create_or_update_user(user):
    method = request.method
    root_created = "users" in data and "root" in data["users"]
    creating_root = not root_created and user == "root" and method == "PUT"

    if not root_created and not creating_root:
        return {
            "type": "problems/root_user_not_created",
            "title": "Root user must be created first",
            "detail": ("The root user must be created with a PUT request "
                       "before doing other operations.")
        }, HTTPStatus.CONFLICT

    if root_created:
        problem, code, headers = require_auth_key(user)
        if problem:
            return problem, code, headers

    if method == "PATCH":
        problem, code = require_user_existence(user)
        if problem:
            return problem, code

    request_data = request.get_json(silent = True) or {}
    validation_problems = []

    if not isinstance(request_data, dict):
        validation_problems.append({
            "reason": "Request body must be a JSON object"
        })
        request_data = {}

    for field in ["timesheet", "schedule", "auth_key"]:
        if field in request_data and not isinstance(request_data[field], str):
            validation_problems.append({
                "field": field,
                "reason": "must be a string"
            })

    for field in ["timesheet", "schedule"]:
        if field in request_data and not _is_external_url(request_data[field]):
            validation_problems.append({
                "field": field,
                "reason": "must be a valid URL"
            })

    if "auth_key" in request_data:
        for problem in validate_auth_key_security(request_data["auth_key"]):
            validation_problems.append({
                "field": "auth_key",
                "reason": problem
            })

    if len(validation_problems) > 0:
        return {
            "type": "problems/user_data_validation",
            "title": "Given user representation did not pass validation",
            "problems": validation_problems
        }, HTTPStatus.BAD_REQUEST

    creating_user = "users" not in data or user not in data["users"]
    generated_auth_key = None
    given_auth_key = None

    if "users" not in data:
        data["users"] = {}

    if method == "PUT":
        data["users"][user] = {}

    if "auth_key" in request_data:
        given_auth_key = request_data["auth_key"]

    if method == "PUT" and "auth_key" not in request_data:
        generated_auth_key = generate_auth_key()

    if given_auth_key or generated_auth_key:
        hashed_auth_key = hash_auth_key(given_auth_key or generated_auth_key)
        data["users"][user]["hashed_auth_key"] = hashed_auth_key

    for field in ["timesheet", "schedule"]:
        if field in request_data:
            data["users"][user][field] = request_data[field]

    raise_data_update()

    user_representation = _get_user_representation(user)
    response_code = HTTPStatus.CREATED if creating_user else HTTPStatus.OK

    if generated_auth_key is not None:
        return user_representation | {
            "auth_key": generated_auth_key,
            "detail": ("The auth key has been generated and is given in "
                       "the 'auth_key' field. Please, keep it in a safe place. "
                       "It will not be shown again.")
        }, response_code

    return user_representation, response_code

@bp.route("/<user>", methods = ["DELETE"])
@auth_key_required
@user_existence_required
def delete_user(user):
    if user == "root":
        return {
            "type": "problems/deleting_root",
            "title": "Not allowed to delete the root user."
        }, HTTPStatus.FORBIDDEN

    del data["users"][user]

    raise_data_update()

    return { "detail": f"The user {user} was deleted." }, HTTPStatus.OK
