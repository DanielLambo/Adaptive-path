# tests/test_full_pipeline.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.security import API_TOKEN

client = TestClient(app)
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

@pytest.fixture
def mock_ml_model(mocker):
    """Mocks the Keras model and scaler to return predictable results."""
    # Mock the Keras model
    mock_model = MagicMock()
    mock_probabilities = [0.1, 0.2, 0.6, 0.05, 0.05]
    mock_model.predict.return_value = [mock_probabilities]
    mocker.patch("tensorflow.keras.models.load_model", return_value=mock_model)

    # Mock the scaler to behave correctly
    mock_scaler = MagicMock()
    # The transform method should return the input array, simulating scaling.
    mock_scaler.transform.side_effect = lambda x: x
    mocker.patch("joblib.load", return_value=mock_scaler)

    # Mock the metadata file
    mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data='{"max_seq_len": 50, "numeric_features": ["score"], "categorical_features_map": {}, "sequence_features": ["score"], "kp_label_encoder": ["KP1", "KP2", "KP3", "KP4", "KP5"]}')
    )
    return mock_model

@pytest.fixture
def mock_neo4j(mocker):
    """Mocks the Neo4j queries to return predictable graph structures."""
    # Mock the driver where it's USED (in app.main) to prevent real connections
    mocker.patch("app.main.get_driver")

    # Mock the query functions
    async def mock_get_kp(driver, kp_id, db):
        return {"id": kp_id, "name": f"KP {kp_id}"}

    async def mock_prereqs(driver, kp_id, db):
        if kp_id == 3:
            return [{"id": 1, "name": "KP 1"}]
        return []

    async def mock_downstream(driver, kp_id, db):
        if kp_id == 3:
            return [{"id": 4, "name": "KP 4"}]
        return []

    mocker.patch("app.queries.get_kp_by_id", side_effect=mock_get_kp)
    mocker.patch("app.queries.prereqs_for", side_effect=mock_prereqs)
    mocker.patch("app.queries.downstream_kps", side_effect=mock_downstream)


def test_full_pipeline_e2e(mock_ml_model, mock_neo4j):
    """
    Tests the full end-to-end flow from API request to response.
    - Uses a mock ML model to control prediction.
    - Uses mock Neo4j queries to control path generation.
    - Does NOT mock the predictor_service or path_builder.
    """
    request_body = {
        "student_id": "e2e-student",
        "history": [
            {"kp_id": 1, "score": 0.9, "type": "quiz"},
            {"kp_id": 2, "score": 0.8, "type": "quiz"},
            {"kp_id": 3, "score": 0.4, "type": "quiz"}, # Low score should lead to KP 3
        ]
    }

    response = client.post("/generate-path", headers=HEADERS, json=request_body)

    assert response.status_code == 200
    data = response.json()

    # 1. Check the prediction part
    assert data["prediction_info"]["kp_id"] == 3 # Our mock model predicts KP 3
    assert data["prediction_info"]["confidence"] == 0.6

    # 2. Check the path builder part
    path_kp_ids = [item["kp_id"] for item in data["learning_path"]]
    # Based on our mock_neo4j, the path should be Prereq(1) -> Target(3) -> Downstream(4)
    assert path_kp_ids == [1, 3, 4]

    # 3. Check that content was retrieved (from mock blackboard)
    target_module = next(item for item in data["learning_path"] if item["kp_id"] == 3)
    assert len(target_module["content"]) > 0
    assert target_module["content"][0]["title"] == "Loops Deep Dive"
