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

from time import time, perf_counter

from kaffee_server.users import get_users, insert_transactions
from kaffee_server.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


def generate_data(start=perf_counter(), sensitive=False) -> dict:
    """Creates a dict with user data and statistics, to be sent to the client"""
    users = get_users(sensitive)

    return {
        "timestamp": time(),
        "sensitive": sensitive,
        "users": users,
        "statistics": {
            "motd": current_app.config.get("MOTD"),
            "beanInfo": current_app.config.get("BEANINFO"),
            "drinkPrice": current_app.config.get("DRINK_PRICE"),
            "contact": current_app.config.get("CONTACT"),
            "queryTime": perf_counter() - start,
        },
    }


def verify_key(api_key: str) -> bool:
    """Verifies an API key in the database"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM clients WHERE api_key = ?) AS result", (api_key,)
    )
    result = cur.fetchone()["result"]
    if not result:
        current_app.logger.warning(f"Key {api_key} is invalid!")
    return result


@bp.route("/")
def api():
    """Return a list of users"""
    return jsonify(generate_data(sensitive=False))


@bp.route("transactions", methods=["POST"])
def process_transactions():
    """Process an array of pending transactions"""
    start = perf_counter()
    data = request.get_json()

    # verify API key
    if not "X-API-KEY" in request.headers or not verify_key(
        request.headers["X-API-KEY"]
    ):
        return jsonify("Error: unauthenticated"), 401

    insert_transactions(data)

    return jsonify(generate_data(start=start, sensitive=True))
