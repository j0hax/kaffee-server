################################################################################
## users.py
################################################################################
## Arbeitet mit der Datenbank zur Kontomanipulation
################################################################################

from time import perf_counter
from flask import current_app
from kaffee_server.db import get_db
from multiprocessing import Pool


def delete_user(id: int):
    """Deletes a user

    Removes the user from the database, however debts are kept.
    """
    current_app.logger.warning(f"Deleting user with ID {id}")
    cur = get_db().cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (id,))
    get_db().commit()


def undo_transaction(id: int):
    """Deletes the last transaction of a user."""
    current_app.logger.warning(f"Deleting transaction with ID {id}")
    with get_db() as cur:
        cur.execute(
            "DELETE FROM transactions WHERE user = ? ORDER BY timestamp DESC LIMIT 1;",
            (id,),
        )


def get_user(id: int, sensitive=True) -> dict:
    if sensitive:
        with get_db() as cur:
            result = cur.execute(
                "SELECT users.id AS userid, * FROM users LEFT JOIN balances ON users.id = balances.id WHERE users.id = ?",
                id,
            ).fetchone()
    else:
        with get_db() as cur:
            result = cur.execute(
                "SELECT users.id AS userid, * FROM users WHERE users.id = ?",
                id,
            )

    if result is None:
        raise ValueError("User ID does not exist")
    else:
        return dict(result)


def get_users(sensitive=True) -> dict:
    """Return a list of users

    These can be directly converted to JSON for the client or used for further processing.
    """
    current_app.logger.debug(f"Retrieving users, include sensitive data: {sensitive}")
    cur = get_db().cursor()
    cur.execute(
        "SELECT users.id AS userid, * FROM users LEFT JOIN balances ON users.id = balances.id WHERE users.id > 0;"
    )
    results = cur.fetchall()
    array = []
    for result in results:
        user_data = {
            "id": result["userid"],
            "vip": result["vip"] or False,
            "name": result["name"],
            "balance": result["balance"] or 0,
            "lastUpdate": result["last_update"],
        }

        # Include sensitive data if requested
        if sensitive:
            user_data["transponder"] = result["transponder_code"]
            user_data["withdrawals"] = result["withdrawal_count"] or 0
            user_data["deposits"] = result["deposit_count"] or 0
            user_data["withdrawalTotal"] = result["withdrawals"] or 0
            user_data["depositTotal"] = result["deposits"] or 0

        array.append(user_data)

    # Sort by VIP Status, then activity
    users_s = sorted(array, key=lambda x: (-x["vip"], x["lastUpdate"]))

    return users_s


def insert_user(user: dict):
    cur = get_db().cursor()

    # Check if user exists
    cur.execute("SELECT * FROM users WHERE id = ?", (user["id"],))
    data = cur.fetchone()
    if data:
        if user["lastUpdate"] > data["last_update"]:
            # update our user
            current_app.logger.info(f"Updating user {user['name']}")
            cur.execute(
                "UPDATE users SET vip=?, name=?, transponder_code=? WHERE id=?",
                (
                    user["vip"],
                    user["name"],
                    user["transponder"],
                    user["id"],
                ),
            )
    else:
        current_app.logger.info(f"Inserting new user {user['name']}")
        cur.execute(
            "INSERT INTO users (vip, name, last_update, transponder_code) VALUES (?, ?,?,?)",
            (
                user["vip"],
                user["name"],
                user["lastUpdate"],
                user["transponder"],
            ),
        )

    get_db().commit()


def merge_users(client_users: list):
    """Compare and update users in the database

    Commonly used to merge cached data returned from a client.
    """
    current_app.logger.debug(f"Merging {len(client_users)}")
    with Pool() as pool:
        pool.map(insert_user, client_users)


def get_transactions(limit=10) -> dict:
    """Return a list of transactions"""
    current_app.logger.debug(f"Retrieving last {limit} transactions")
    cur = get_db().cursor()
    cur.execute(
        "SELECT name, amount, description, timestamp FROM transactions LEFT JOIN users ON transactions.user = users.id ORDER BY timestamp DESC LIMIT ?;",
        (limit,),
    )
    return cur.fetchall()


def sum_transactions() -> int:
    """Sums all transactions"""
    start_time = perf_counter()
    cur = get_db().cursor()
    cur.execute("SELECT SUM(amount) from transactions;")
    current_app.logger.debug(
        f"Summing all transactions took {perf_counter() - start_time} milliseconds"
    )
    return cur.fetchone()[0]


def insert_transactions(pending: list):
    """Insert a list of transactions"""
    current_app.logger.debug(f"Inserting {len(pending)} transactions")
    with Pool() as pool:
        pool.map(insert_transaction, pending)


def insert_transaction(transaction: dict):
    """Insert a transaction into the database"""

    user = transaction["user"]
    amount = transaction["amount"]
    description = transaction["description"]
    timestamp = transaction["timestamp"]

    current_app.logger.info(f"Booking {amount / 100} towards user ID {user}")

    cur = get_db().cursor()
    # Insert transaction
    cur.execute(
        "INSERT INTO transactions VALUES (?,?,?,?)",
        (
            user,
            amount,
            description,
            timestamp,
        ),
    )
    get_db().commit()
