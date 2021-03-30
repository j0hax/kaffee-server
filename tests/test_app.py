import json

import sqlite3
from main import app, get_db

def test_start():
    response = app.test_client().get("/api")

    assert response.status_code == 200

def test_database():
    cur = sqlite3.connect('coffee.db').cursor()
    qry = open("tests/test_row.sql", "r").read()
    cur.executescript(qry)
    cur.close()

def test_read():
    response = app.test_client().get("/api")
    data = json.loads(response.data.decode())
    assert isinstance(data, list)


def test_update():
    payload = [{"balance":9000,"drinkCount":30,"hash":"9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08","id":1,"lastUpdate":1616759150.347016,"name":"Test User"}]
    update_payload = [{"balance":9000,"drinkCount":31,"hash":"9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08","id":1,"lastUpdate":1616759150.347016,"name":"Test User"}]
    
    # Insert user data
    response = app.test_client().post("/api", json = { "apiKey":"ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6", "users": payload})
    data = json.loads(response.data.decode())
    
    # Ignore timestamps
    for d in data:
        del d["lastUpdate"]
    del payload[0]["lastUpdate"]
    
    assert payload[0] in data
    
    # Changed data for same user
    response = app.test_client().post("/api", json = { "apiKey":"ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6", "users": update_payload})
    data = json.loads(response.data.decode())
    
    # Ignore timestamps
    for d in data:
        del d["lastUpdate"]
    del update_payload[0]["lastUpdate"]
    
    assert payload[0] not in data
    assert update_payload[0] in data
