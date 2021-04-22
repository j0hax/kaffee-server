import json

import sqlite3
import random
import time
from main import app, get_db
import tempfile

app.config["DATABASE"] = tempfile.NamedTemporaryFile(delete=False).name
print("Using", app.config["DATABASE"])


def test_start():
    response = app.test_client().get("/api")

    assert response.status_code == 200


def test_read():
    response = app.test_client().get("/api")
    data = json.loads(response.data.decode())
    assert isinstance(data, list)


def test_transaction():
    """ Write thousands of test transactions"""

    # 10000 requests
    for i in range(1000):
        payload = []

        # Each with 1 - 100 pending transaction
        for i in range(random.randint(1, 100)):
            # 1% chance that a user will deposit between 1 and 50 EUR
            amount = 0
            if random.random() < (1 / 100):
                amount = random.randint(1, 50) * 100
            else:
                amount = -30

            payload.append(
                {
                    "user": random.randint(1, 100),
                    "amount": amount,
                    "description": "AUTOMATED",
                    "timestamp": time.time(),
                }
            )

        # Insert user data
        response = app.test_client().post(
            "/api/transactions",
            json={
                "apiKey": "ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6",
                "transactions": payload,
            },
        )

        # Shouldn't be a problem
        assert response.status_code == 200
