#!/usr/bin/env python3
import locale
import sqlite3
import time
import os
from datetime import datetime
from flask import Flask, flash, g, jsonify, redirect, render_template, request
from flask_cors import CORS
from icecream import ic
import bcrypt
import flask_login


class User(flask_login.UserMixin):
    def check_password(self, password):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM admins WHERE username = ?", (self.id,))
        data = cur.fetchone()
        return bcrypt.checkpw(password.encode(), data[1].encode())


app = Flask(__name__)
CORS(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.config.from_object("config.ProductionConfig")

# Create a secret key
app.secret_key = os.urandom(16)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        cur = db.cursor()
        qry = open("create_tables.sql", "r").read()
        cur.executescript(qry)
        cur.close()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("overview.html", users=get_users())


@login_manager.user_loader
def load_user(user_id):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM admins WHERE username = ?", (user_id,))
    data = cur.fetchone()
    if not data:
        return None

    user = User()
    user.id = data[0]

    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    user = load_user(request.form["username"])

    if user and user.check_password(request.form["password"]):
        flask_login.login_user(user)
        flash("Erfolgreich eingeloggt als " + user.get_id())
        return redirect("/admin")
    else:
        flash("Falscher Nutzer oder Passwort")
        return redirect("/login")


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/login?next=" + request.path)


@app.route("/admin")
@flask_login.login_required
def admin():
    ic("Entered admin page")
    return render_template("admin.html", users=get_users())


@app.route("/admin/save/user", methods=["POST"])
@flask_login.login_required
def savetable():

    if request.form["action"] == "delete":
        delete_user(request.form["id"])
        flash("Deleted user " + request.form["name"])
        return redirect("/admin")

    ic("Saving table")

    # Update our balance
    payment = int(float(request.form["payment"]) * 100)
    balance = int(float(request.form["balance"]) * 100) + payment

    # Assume we are getting one row
    user = [
        {
            "id": request.form["id"],
            "name": request.form["name"],
            "balance": balance,
            "drinkCount": request.form["drink_count"],
            "lastUpdate": time.time(),
            "hash": request.form["transponder_hash"],
        }
    ]

    flash("Updated user " + request.form["name"])

    merge_users(user)

    return redirect("/admin")


@app.route("/api", methods=["POST", "GET"])
def api():
    """Update or return an array of user statistics"""
    if request.method == "GET":
        """return a list of users"""
        return jsonify(get_users())

    if request.method == "POST":
        """modify/update the user database"""
        print("Recieved data:", end=" ")
        # verify API key
        data = request.get_json()
        if not verify_key(data["apiKey"]):
            print("Unauthorized request")
            return jsonify("Error: unauthenticated"), 401

        print("authorized")
        merge_users(data["users"])
        return jsonify(get_users())


@app.route("/api/transactions", methods=["POST"])
def process_transactions():
    """Process an array of pending transactions"""
    print("Recieved data:", end=" ")
    # verify API key
    data = request.get_json()
    if not verify_key(data["apiKey"]):
        print("Unauthorized request")
        return jsonify("Error: unauthenticated"), 401

    print("authorized")
    insert_transactions(data["transactions"])
    return jsonify(get_users())


def verify_key(api_key):
    """Verifies an API key in the database"""
    cur = get_db().cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM clients WHERE api_key = ?)", (api_key,))
    return cur.fetchone()[0]


def delete_user(id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM users WHERE rowid = ?", (id,))
    get_db().commit()


def get_user_balance(id):
    cur = get_db().cursor()
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user = ", (id,))
    return cur.fetchone()[0]


def merge_users(client_users):
    """Compare and update users in the database via those from the client"""
    ic("Merging users...")
    cur = get_db().cursor()
    for user in client_users:
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE rowid = ?", (user["id"],))
        data = cur.fetchone()

        if data:
            if user["lastUpdate"] > data[3]:
                # update our user
                print("Updating user", data[0])
                cur.execute(
                    "UPDATE users SET name=?,balance=?,drink_count=?,last_update=?,transponder_hash=? WHERE rowid=?",
                    (
                        user["name"],
                        user["balance"],
                        user["drinkCount"],
                        time.time(),
                        user["hash"],
                        user["id"],
                    ),
                )
            else:
                print("Found but not updating user", data[0])
        else:
            print("Inserting user", user["name"])
            cur.execute(
                "INSERT INTO users VALUES (?,?,?,?,?)",
                (
                    user["name"],
                    user["balance"],
                    user["drinkCount"],
                    user["lastUpdate"],
                    user["hash"],
                ),
            )

    get_db().commit()


def insert_transactions(pending: list):
    """Insert a list of transactions"""
    for transaction in pending:
        insert_transaction(transaction)


def insert_transaction(transaction: dict):
    """Insert a transaction into the database"""
    ic(transaction)
    cur = get_db().cursor()
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


@app.template_filter("from_cents")
def from_cents(cents):
    return cents / 100


@app.template_filter("pretty_currency")
def pretty_currency(cents):
    return locale.currency(from_cents(cents))


@app.template_filter("pretty_date")
def pretty_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%a, %x um %X")


@app.template_filter("pretty_number")
def pretty_number(number):
    return locale.format("%d", number, grouping=True)


def get_users():
    """Return users as a JSON Array"""
    cur = get_db().cursor()
    cur.execute("SELECT rowid, * FROM users ORDER BY drink_count DESC")
    results = cur.fetchall()
    array = []
    for result in results:
        array.append(
            {
                "id": result[0],
                "name": result[1],
                "balance": result[2],
                "drinkCount": result[3],
                "lastUpdate": result[4],
                "hash": result[5],
            }
        )

    ic("Retrieved list of users")
    return array


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "de_DE")

    import bjoern

    bjoern.run(app, "", 8080)
