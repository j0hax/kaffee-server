################################################################################
## admin.py
################################################################################
## REST-Schnittstelle
################################################################################

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
)

from time import time

from kaffee_server.users import get_users, insert_transactions
from kaffee_server.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


def generate_data(start=time()) -> dict:
    """Creates a dict with user data and statistics, to be sent to the client"""
    users = get_users()
    return {
        "users": users,
        "statistics": {
            "drinkPrice": current_app.config["DRINK_PRICE"],
            "queryTime": time() - start,
        },
    }


def verify_key(api_key: str) -> bool:
    """Verifies an API key in the database"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM clients WHERE api_key = ?) AS result", (api_key,)
    )
    return cur.fetchone()["result"]


@bp.route("/")
def api():
    """Return a list of users"""
    start = time()
    return jsonify(generate_data(start))


@bp.route("transactions", methods=["POST"])
def process_transactions():
    """Process an array of pending transactions"""
    start = time()
    data = request.get_json()

    # verify API key
    if not "X-API-KEY" in request.headers or not verify_key(
        request.headers["X-API-KEY"]
    ):
        print("Unauthorized request")
        return jsonify("Error: unauthenticated"), 401

    insert_transactions(data)

    return jsonify(generate_data(start))
