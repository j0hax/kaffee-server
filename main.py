#!/usr/bin/env python3
import locale
import sqlite3
import time
import os
from datetime import datetime
from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
)
from flask_cors import CORS
from icecream import ic
import bcrypt
import flask_login
import csv
import tempfile


class User(flask_login.UserMixin):
    def check_password(self, password):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM admins WHERE username = ?", (self.id,))
        data = cur.fetchone()
        return bcrypt.checkpw(password.encode(), data["pw_hash"].encode())


app = Flask(__name__)
CORS(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.config.from_object("config.ProductionConfig")

# Create a secret key
app.secret_key = os.urandom(16)


def get_db():
    def dict_factory(cursor, row):
        """ Returns a dict for a selected row """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = dict_factory
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
    user.id = data["username"]

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
    return render_template("admin.html", users=get_users())


@app.route("/admin/dump/users")
def dump_users():
    """Downloads a CSV of user data"""
    outfile = tempfile.NamedTemporaryFile(mode="w")
    users = get_users()

    dict_writer = csv.DictWriter(outfile, users[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(users)
    outfile.flush()

    return send_file(outfile.name, as_attachment=True, attachment_filename="users.csv")


@app.route("/admin/save/user", methods=["POST"])
@flask_login.login_required
def savetable():
    if request.form["action"] == "delete":
        delete_user(request.form["id"])
        flash("Deleted user " + request.form["name"])
        return redirect("/admin")

    # Assume we are getting one row
    user = [
        {
            "id": request.form["id"],
            "name": request.form["name"],
            "lastUpdate": time.time(),
            "hash": request.form["transponder_hash"],
        }
    ]

    merge_users(user)

    # Check if a deposit was made
    if "payment" in request.form:
        # TODO: ensure there are no float innaccuracies
        payment = round(float(request.form["payment"]) * 100)
        if payment > 0:
            db = get_db()
            c = db.cursor()
            c.execute(
                "INSERT INTO transactions (user, amount, description) VALUES (?,?,?)",
                (user[0]["id"], payment, "Einzahlung durch Adminbereich"),
            )
            db.commit()

    flash("Updated user " + request.form["name"])
    return redirect("/admin")


@app.route("/api")
def api():
    """Update or return an array of user statistics"""
    if request.method == "GET":
        """return a list of users"""
        return jsonify(get_users())


@app.route("/api/transactions", methods=["POST"])
def process_transactions():
    """Process an array of pending transactions"""

    data = request.get_json()

    # verify API key
    if not verify_key(request.headers["X-API-KEY"]):
        print("Unauthorized request")
        return jsonify("Error: unauthenticated"), 401

    insert_transactions(data)
    return jsonify(get_users())


def verify_key(api_key: str):
    """Verifies an API key in the database"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM clients WHERE api_key = ?) AS result", (api_key,)
    )
    return cur.fetchone()["result"]


def delete_user(id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM users WHERE rowid = ?", (id,))
    get_db().commit()


def merge_users(client_users):
    """Compare and update users in the database via those from the client"""
    cur = get_db().cursor()
    for user in client_users:
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE rowid = ?", (user["id"],))
        data = cur.fetchone()

        if data:
            if user["lastUpdate"] > data["last_update"]:
                # update our user
                print("Updating user", data["name"])
                cur.execute(
                    "UPDATE users SET name=?,transponder_hash=? WHERE rowid=?",
                    (
                        user["name"],
                        user["hash"],
                        user["id"],
                    ),
                )
            else:
                print("Found but not updating user", data[0])
        else:
            print("Inserting user", user["name"])
            cur.execute(
                "INSERT INTO users VALUES (?,?,?)",
                (
                    user["name"],
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


@app.template_filter("from_cents")
def from_cents(cents):
    if not cents:
        return 0
    return cents / 100


@app.template_filter("pretty_currency")
def pretty_currency(cents):
    return locale.currency(from_cents(cents))


@app.template_filter("pretty_date")
def pretty_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%a, %x um %X")


@app.template_filter("pretty_number")
def pretty_number(number):
    return locale.format_string("%d", number, grouping=True)


def get_users():
    """Return users with balances as a JSON Array"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT users.rowid, * FROM users LEFT JOIN balances ON users.rowid = balances.id ORDER BY withdrawal_count DESC"
    )
    results = cur.fetchall()
    array = []
    for result in results:
        array.append(
            {
                "id": result["rowid"],
                "name": result["name"],
                "balance": result["balance"] or 0,
                "withdrawalCount": result["withdrawal_count"] or 0,
                "depositCount": result["deposit_count"] or 0,
                "withdrawals": result["withdrawals"] or 0,
                "deposits": result["deposits"] or 0,
                "lastUpdate": result["last_update"],
                "hash": result["transponder_hash"],
            }
        )

    return array


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "de_DE")

    import bjoern

    bjoern.run(app, "", 8080)
