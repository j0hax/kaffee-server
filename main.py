#!/usr/bin/env python3
import configparser
import locale
import sqlite3
import time

from flask import Flask, g, jsonify, redirect, render_template, request
from flask_cors import CORS
from icecream import ic

app = Flask(__name__)
CORS(app)

config = configparser.ConfigParser()
config.read("config.ini")

DATABASE = config["database"]["file"]


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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


@app.route('/admin')
def admin():
    ic("Entered admin page")
    return render_template("admin.html", users=get_users())


@app.route("/api", methods=["POST", "GET"])
def api():
    if request.method == "GET":
        """return a list of users"""
        return jsonify(get_users())

    if request.method == "POST":
        """modify/update the user database"""
        # verify API key
        data = request.get_json()
        if not verify_key(data["apiKey"]):
            print("Unauthorized request")
            return jsonify("Error: unauthenticated"), 401

        merge_users(data['users'])
        return jsonify(get_users())


def verify_key(api_key):
    """Verifies an API key in the database"""
    cur = get_db().cursor()
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM clients WHERE api_key = ?)", (api_key,))
    return cur.fetchone()[0]


def merge_users(client_users):
    """Compare and update users in the database via those from the client"""
    ic("Merging users...")
    cur = get_db().cursor()
    for user in client_users:
        # Check if user exists
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE rowid = ?)", (user["id"],))
        exists = cur.fetchone()[0]

        if exists:
            # update our user
            print("Updating user", user["name"])
            cur.execute(
                "UPDATE users SET name=?,balance=?,drink_count=?,last_update=?,transponder_hash=? WHERE rowid=?",
                (user["name"],
                 user["balance"],
                    user["drinkCount"],
                    time.time(),
                    user["hash"],
                    user["id"]))
        else:
            print("Inserting user", user["name"])
            cur.execute(
                "INSERT INTO users VALUES (?,?,?,?,?)",
                (user["name"],
                 user["balance"],
                    user["drinkCount"],
                    user["lastUpdate"],
                    user["hash"]))

    get_db().commit()


@app.template_filter('format_cents')
def format_currency(cents):
    return locale.currency(cents / 100)


def get_users():
    """Return users as a JSON Array"""
    cur = get_db().cursor()
    cur.execute("SELECT rowid, * FROM users")
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

    bjoern.run(app, "", 80)
