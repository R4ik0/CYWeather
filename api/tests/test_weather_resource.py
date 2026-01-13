import httpx
from unittest.mock import patch, AsyncMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.resources.weather_resource import router

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def test_get_current_weather_city_not_found(client):
    response_404 = httpx.Response(status_code=404)

    with patch(
        "src.resources.weather_resource.weather_service.get_current_weather",
        new_callable=AsyncMock
    ) as mock_service:
        mock_service.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=httpx.Request("GET", "http://test"),
            response=response_404,
        )

        response = client.get("/weather/current?city=UnknownCity")

        assert response.status_code == 404
        assert "non trouvée" in response.json()["detail"]


def test_get_current_weather_http_error(client):
    with patch(
        "src.resources.weather_resource.weather_service.get_current_weather",
        new_callable=AsyncMock
    ) as mock_service:
        mock_service.side_effect = httpx.HTTPError("API error")

        response = client.get("/weather/current?city=Paris")

        assert response.status_code == 500
        assert "Erreur de connexion" in response.json()["detail"]
