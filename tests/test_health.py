import requests

from conftest import ROOT_URL


def test_api_is_healthy():
    """Шаг 1 плана: убедиться, что система поднята и API отвечает."""
    response = requests.get(f"{ROOT_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
