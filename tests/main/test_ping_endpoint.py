import pytest


class TestEndpointsSynchronous:

    def test_root_404(self, client):
        response = client.get('/')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}

    def test_ping(self, client):
        response = client.get('/ping')
        assert response.status_code == 200
        assert response.json() == {'ping': 'pong!'}


@pytest.mark.asyncio
class TestEndPointsAsync:

    async def test_root_404(self, async_client):
        response = await async_client.get('/')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}

    async def test_ping(self, async_client):
        response = await async_client.get('/ping')
        assert response.status_code == 200
        assert response.json() == {'ping': 'pong!'}
