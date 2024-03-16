from flask import Blueprint

from .auth import auth_key_required

bp = Blueprint("hello", __name__, url_prefix="/v1/<user>/hello")

@bp.route("/", methods = ["GET"], strict_slashes = False)
@auth_key_required
def say_hello(user):
    return {
        "message": f"Hello, {user}!"
    }
