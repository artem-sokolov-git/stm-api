from collections.abc import Generator

import httpx
import pytest
from fastapi.testclient import TestClient

from core.config import settings
from core.main import app

ROUTE_ID = "24"  # Sherbrooke — stable STM bus route


@pytest.fixture
def client() -> httpx.Client:
    return httpx.Client(
        headers={"apikey": settings.token.get_secret_value()},
    )


@pytest.fixture(scope="module")
def app_client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c
