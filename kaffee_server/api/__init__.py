################################################################################
## admin.py
################################################################################
## REST-Schnittstelle
################################################################################

from flask import Blueprint, request, jsonify, current_app, redirect, url_for

from time import time, perf_counter
from werkzeug.exceptions import HTTPException
from kaffee_server.users import get_users, insert_transactions
from kaffee_server.db import get_db
from time import time
import kaffee_server.api.v1 as v1

from uuid import uuid4

bp = Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(v1.bp)


@bp.route("/")
def entry():
    return redirect(url_for(".version1.api"))


"""
@bp.app_errorhandler(404)
@bp.app_errorhandler(500)
def handle_api(error):
    if isinstance(error, HTTPException):
        response = {
            "code": error.code,
            "name": error.name,
            "description": error.description,
            "url": request.path,
            "type": str(type(error)),
            "time": time(),
            "id": uuid4(),
        }
        return jsonify(response), error.code
"""