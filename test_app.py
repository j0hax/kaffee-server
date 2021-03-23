import json

from main import app


def test_start():
    response = app.test_client().get('/api')

    assert response.status_code == 200


def test_read():
    response = app.test_client().get('/api')
    data = json.loads(response.data.decode())
    assert isinstance(data, list)
