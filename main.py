#!/usr/bin/env python3
import configparser
import sqlite3

from flask import Flask, g, jsonify, redirect, request
from flask_cors import CORS

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
        qry = open("create_table.sql", "r").read()
        cur.execute(qry)
        cur.close()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return redirect("/api")


@app.route("/api", methods=["POST", "GET"])
def api():
    if request.method == "GET":
        """return a list of users"""
        return jsonify(get_users())

    if request.method == "POST":
        """modify/update the user database"""
        return jsonify(get_users())


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
    return array


if __name__ == "__main__":
    app.run(debug=True)
