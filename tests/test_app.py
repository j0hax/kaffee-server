import json

import sqlite3
import time
from main import app, get_db


def test_start():
    response = app.test_client().get("/api")

    assert response.status_code == 200
    

def test_read():
    response = app.test_client().get("/api")
    data = json.loads(response.data.decode())
    assert isinstance(data, list)


def test_transaction():

    payload = [
            {
                "user": 1,
                "amount": -30,
                "description": "test 1",
                "timestamp": time.time(),
            },
            {
                "user": 2,
                "amount": -30,
                "description": "test 2",
                "timestamp": time.time(),
            }
    ]

    # Insert user data
    response = app.test_client().post(
        "/api/transactions",
        json={
            "apiKey": "ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6",
            "transactions": payload})
    data = json.loads(response.data.decode())
