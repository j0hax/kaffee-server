################################################################################
## users.py
################################################################################
## Arbeitet mit der Datenbank zur Kontomanipulation
################################################################################

from kaffee_server.db import get_db


def delete_user(id: int):
    """Deletes a user

    Removes the user from the database, however debts are kept.
    """
    cur = get_db().cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (id,))
    get_db().commit()


def undo_transaction(id: int):
    """Deletes the last transaction of a user."""
    with get_db() as cur:
        cur.execute(
            "DELETE FROM transactions WHERE user = ? ORDER BY timestamp DESC LIMIT 1;",
            (id,),
        )


def get_users(sensitive=True) -> dict:
    """Return a list of users

    These can be directly converted to JSON for the client or used for further processing.
    """
    cur = get_db().cursor()
    cur.execute(
        "SELECT users.id AS userid, * FROM users LEFT JOIN balances ON users.id = balances.id WHERE users.id > 0 ORDER BY withdrawal_count DESC;"
    )
    results = cur.fetchall()
    array = []
    for result in results:
        user_data = {
            "id": result["userid"],
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

    return array


def merge_users(client_users: list):
    """Compare and update users in the database

    Commonly used to merge cached data returned from a client.
    """
    cur = get_db().cursor()
    for user in client_users:
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE id = ?", (user["id"],))
        data = cur.fetchone()

        if data:
            if user["lastUpdate"] > data["last_update"]:
                # update our user
                cur.execute(
                    "UPDATE users SET name=?,transponder_code=? WHERE id=?",
                    (
                        user["name"],
                        user["transponder"],
                        user["id"],
                    ),
                )
        else:
            cur.execute(
                "INSERT INTO users (name, last_update, transponder_code) VALUES (?,?,?)",
                (
                    user["name"],
                    user["lastUpdate"],
                    user["transponder"],
                ),
            )

    get_db().commit()


def get_transactions(limit=10) -> dict:
    """Return a list of transactions"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT name, amount, description, timestamp FROM transactions LEFT JOIN users ON transactions.user = users.id ORDER BY timestamp DESC LIMIT ?;",
        (limit,),
    )
    return cur.fetchall()


def sum_transactions() -> int:
    """Sums all transactions"""
    cur = get_db().cursor()
    cur.execute("SELECT SUM(amount) from transactions;")
    return cur.fetchone()[0]


def insert_transactions(pending: list):
    """Insert a list of transactions"""
    for transaction in pending:
        insert_transaction(transaction)


def insert_transaction(transaction: dict):
    """Insert a transaction into the database"""
    cur = get_db().cursor()
    # Insert transaction
    cur.execute(
        "INSERT INTO transactions VALUES (?,?,?,?)",
        (
            transaction["user"],
            transaction["amount"],
            transaction["description"],
            transaction["timestamp"],
        ),
    )
    get_db().commit()
