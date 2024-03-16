from http import HTTPStatus
from base64 import b64encode
from weakref import WeakKeyDictionary

import pytest

from app import create_app

_ROOT_AUTH_HEADERS = WeakKeyDictionary()

class CouldNotCreateRootUserError(Exception):
    pass

def _get_basic_auth_string(username, password):
    credentials = f"{username}:{password}"
    credentials_base64 = b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {credentials_base64}"

def _get_auth_headers(username, password):
    return {"Authorization": _get_basic_auth_string(username, password)}

@pytest.fixture()
def app():
    test_app = create_app()
    test_app.testing = True
    return test_app

@pytest.fixture()
def client(app):
    with app.test_client() as client:
        return client

@pytest.fixture()
def data(app):
    with app.app_context():
        from app.data import get_data
        return get_data()

@pytest.fixture()
def auth_headers():
    return _get_auth_headers
