#!/usr/bin/env python3
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

import sqlite3

app = Flask(__name__)
CORS(app)

test = {
            "name": "Johannes Arnold",
            "drinkCount": 42,
            "balance": 9000,
            "lastUpdate": 1614867820842
        }

@app.route('/')
def index():
    return redirect("/api")

@app.route('/api', methods = ['POST', 'GET'])
def api():
    if request.method == 'GET':
        """return a list of users"""
        return jsonify([test])
    
    if request.method == 'POST':
        """modify/update the user database"""
        return jsonify("OK")

if __name__ == '__main__':
    app.run(debug=True)
    con = sqlite3.connect('coffee.db')
