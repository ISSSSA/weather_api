import pytest
from fastapi.testclient import TestClient
from main import app
from app.db_methods import init_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_register_user_success(client):
    response = client.post("/register", json={"username": "testuser"})
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_add_city_success(client):
    user_response = client.post("/register", json={"username": "cityuser"})
    user_id = user_response.json()["user_id"]

    city_payload = {
        "user_id": user_id,
        "city": "London",
        "lat": 51.5074,
        "lon": -0.1278
    }
    response = client.post("/city", json=city_payload)
    assert response.status_code == 200
    assert response.json()["message"] == f"City London added for user {user_id} and weather data saved."


def test_add_city_invalid_user(client):
    city_payload = {
        "user_id": 999,
        "city": "London",
        "lat": 51.5074,
        "lon": -0.1278
    }
    response = client.post("/city", json=city_payload)
    assert response.status_code == 404


def test_get_weather_at_time(client):
    user_response = client.post("/register", json={"username": "weatheruser"})
    user_id = user_response.json()["user_id"]
    client.post("/city", json={
        "user_id": user_id,
        "city": "London",
        "lat": 51.5074,
        "lon": -0.1278
    })

    response = client.get(
        "/weather_at_time",
        params={
            "user_id": user_id,
            "city": "London",
            "time": "2025-01-17T14:00:00",
            "temperature": "true",
            "humidity": "true",
            "wind_speed": "true",
            "pressure": "true"
        }
    )
    assert response.status_code == 200
    assert "temperature" in response.json()
    assert "humidity" in response.json()


def test_weather_at_time_invalid_user(client):
    response = client.get(
        "/weather_at_time",
        params={
            "user_id": 999,
            "city": "London",
            "time": "2025-01-16T14:00:00"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User with ID 999 not found."


def test_list_cities(client):
    user_response = client.post("/register", json={"username": "listcitiesuser"})
    user_id = user_response.json()["user_id"]

    client.post("/city", json={
        "user_id": user_id,
        "city": "Paris",
        "lat": 48.8566,
        "lon": 2.3522
    })
    client.post("/city", json={
        "user_id": user_id,
        "city": "Berlin",
        "lat": 52.52,
        "lon": 13.405
    })

    response = client.get("/cities", params={"user_id": user_id})
    assert response.status_code == 200
    assert len(response.json()["cities"]) == 2
    assert {"city": "Paris", "lat": 48.8566, "lon": 2.3522} in response.json()["cities"]
    assert {"city": "Berlin", "lat": 52.52, "lon": 13.405} in response.json()["cities"]
