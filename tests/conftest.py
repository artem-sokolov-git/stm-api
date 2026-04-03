import httpx
import pytest

from core.config import settings


@pytest.fixture
def client() -> httpx.Client:
    return httpx.Client(
        headers={"apikey": settings.token.get_secret_value()},
    )
