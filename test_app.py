from main import app

def test_start():
    response = app.test_client().get('/api')

    assert response.status_code == 200
