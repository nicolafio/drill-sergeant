from weakref import WeakKeyDictionary

import pytest

from app import create_app

_ROOT_AUTH_HEADERS = WeakKeyDictionary()

class CouldNotCreateRootUserError(Exception):
    pass

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
