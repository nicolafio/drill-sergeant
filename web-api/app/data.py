from os import path
from weakref import WeakKeyDictionary
from weakref import WeakSet

import json
from flask import Blueprint
from flask import current_app
from werkzeug.local import LocalProxy

# (i.) Using dictionaries to avoid single global variables, hence allowing
# multiple applications with their own data to exist.
# (ii.) Using *weak* dictionaries/sets so that when the app clears from memory,
# so does the related data.
_DATA = WeakKeyDictionary()
_DATA_FILE_PATHS = WeakKeyDictionary()
_DATA_NEEDS_SAVING = WeakSet()

bp = Blueprint("data", __name__)

def _get_app_ref(app):
    if isinstance(app, LocalProxy):
        # `app` is a werkzeug.local.LocalProxy, but we need to get the actual
        # object to use it as a key for the weak dictionaries used to store data.
        return app._get_current_object() #pylint: disable=protected-access

    return app

def get_data(app = current_app):
    ref = _get_app_ref(app)

    if ref not in _DATA:
        app_data = None
        file_path = path.realpath(path.join(app.root_path, "..", ".data.json"))

        _DATA_FILE_PATHS[ref] = file_path

        try:
            file = open(file_path, encoding = "utf-8")
        except FileNotFoundError:
            app_data = dict()
        else:
            with file:
                app_data = json.load(file)

        _DATA[ref] = app_data

    return _DATA[ref]

def save_data(app = current_app):
    ref = _get_app_ref(app)

    _DATA_NEEDS_SAVING.add(ref)

data = LocalProxy(get_data)

@bp.after_app_request
def _after_request(response):
    ref = _get_app_ref(current_app)

    if ref in _DATA_NEEDS_SAVING:
        if not current_app.testing:
            with open(_DATA_FILE_PATHS[ref], "w+", encoding="utf-8") as file:
                json.dump(
                    obj = _DATA[ref],
                    fp = file,
                    indent = 4,
                    sort_keys = True,
                    ensure_ascii = False
                )

        _DATA_NEEDS_SAVING.remove(ref)

    return response
