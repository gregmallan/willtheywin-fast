import pytest

from fastapi.testclient import TestClient

from src.main import app as fast_api_app


def pytest_report_header(config):
    return ["PROJECT: willtheywin-fast", ]


@pytest.fixture
def app():
    return fast_api_app


@pytest.fixture
def client(app):
    return TestClient(app)
