def test_root_404(client):
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_ping(client):
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.json() == {'ping': 'pong!'}
