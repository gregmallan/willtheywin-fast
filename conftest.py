import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app as fast_api_app


def pytest_report_header(config):
    return ["PROJECT: willtheywin-fast", ]


@pytest.fixture
def app():
    return fast_api_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url='http://') as client:
        yield client
