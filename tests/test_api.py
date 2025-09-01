# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security import API_TOKEN

client = TestClient(app)

# Use a fixed token for testing
TEST_TOKEN = API_TOKEN
HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}


def test_health_check():
    """Tests the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_path_success(mocker):
    """
    Tests the main success path of the /generate-path endpoint.
    It mocks the predictor and the path builder to isolate the API layer.
    """
    # Mock the Neo4j driver to prevent it from trying to connect
    mocker.patch("app.main.get_driver")

    # Mock the predictor service to return a deterministic result
    mock_pred = {
        "student_id": "student-123", "top_kp": 3, "confidence": 0.9,
        "top3": [(3, 0.9), (1, 0.05), (2, 0.05)], "message": "Prediction successful."
    }
    mocker.patch("app.main.get_pred_for_student", return_value=mock_pred)

    # Mock the path builder to return a sample path
    mock_path = [
        {"kp_id": 1, "kp_name": "Prereq KP", "content": []},
        {"kp_id": 3, "kp_name": "Target KP", "content": []},
    ]
    mocker.patch("app.main.build_path_for_kp", return_value=mock_path)

    request_body = {
        "student_id": "student-123",
        "history": [{"kp_id": 1, "score": 0.8, "type": "quiz"}]
    }

    response = client.post("/generate-path", headers=HEADERS, json=request_body)

    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "student-123"
    assert data["prediction_info"]["kp_id"] == 3
    assert len(data["learning_path"]) == 2


def test_generate_path_no_auth():
    """Tests that the endpoint is protected."""
    request_body = {"student_id": "student-123", "history": []}
    response = client.post("/generate-path", json=request_body)
    # It should fail because the Authorization header is missing
    assert response.status_code == 401


def test_generate_path_invalid_token():
    """Tests that the endpoint rejects an invalid token."""
    request_body = {"student_id": "student-123", "history": []}
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.post("/generate-path", headers=headers, json=request_body)
    assert response.status_code == 403


def test_generate_path_kp_not_found(mocker):
    """
    Tests the 404 Not Found case when a path cannot be built.
    """
    # Mock the Neo4j driver
    mocker.patch("app.main.get_driver")

    # Mock the predictor to return a valid KP
    mock_pred = {"top_kp": 999, "confidence": 0.9, "top3": [(999, 0.9)]}
    mocker.patch("app.main.get_pred_for_student", return_value=mock_pred)

    # Mock the path builder to return an empty list, simulating a not-found KP
    mocker.patch("app.main.build_path_for_kp", return_value=[])

    request_body = {
        "student_id": "student-123",
        "history": [{"kp_id": 1, "score": 0.8, "type": "quiz"}]
    }

    response = client.post("/generate-path", headers=HEADERS, json=request_body)

    assert response.status_code == 404
    assert "Could not build a path" in response.json()["detail"]
