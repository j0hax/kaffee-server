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


def to_camel_case(snake: str) -> str:
    # Helper function to convert snake case to camelcase
    components = snake.split("_")
    return components[0].lower() + "".join(x.title() for x in components[1:])


@bp.route("/")
def entry():
    return redirect(url_for(".version1.api"))
