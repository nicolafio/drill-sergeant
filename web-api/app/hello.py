from flask import Blueprint

from .auth import auth_key_required
from .user import bp as user_bp

bp = Blueprint("hello", __name__, url_prefix = user_bp.url_prefix)

@bp.route("/<user>/hello", methods = ["GET"], strict_slashes = False)
@auth_key_required
def _say_hello(user):
    return {
        "message": f"Hello, {user}!"
    }
