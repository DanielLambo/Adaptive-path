# tests/test_model_service_fallback.py
import pytest
from app import model_service

# Reset the service state before each test to ensure isolation
@pytest.fixture(autouse=True)
def reset_services():
    """Ensures each test runs with a clean service state."""
    model_service._services["loaded"] = False
    model_service._services["model"] = None
    model_service._services["scaler"] = None
    model_service._services["metadata"] = None

def test_fallback_activates_when_model_is_missing(mocker):
    """
    Ensures the fallback is used if model/scaler files can't be loaded.
    This test patches the loading functions directly to simulate missing files.
    """
    # Simulate files not being found by patching the loaders
    mocker.patch("tensorflow.keras.models.load_model", side_effect=FileNotFoundError)
    mocker.patch("joblib.load", side_effect=FileNotFoundError)

    # We still need to mock open for the metadata file since it's gitignored
    mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data='{"max_seq_len": 50, "numeric_features": [], "categorical_features_map": {}, "sequence_features": [], "kp_label_encoder": ["KP1", "KP2"] }'),
    )

    mock_logger_warning = mocker.patch("app.model_service.logger.warning")

    history = [{"kp_id": 1, "score": 0.9}, {"kp_id": 2, "score": 0.4}]
    top_kp, _, _ = model_service.predict_weakest_kp(history)

    # Assert that the warnings for missing files were logged
    mock_logger_warning.assert_any_call(f"⚠️ Feature scaler not found at {model_service.SCALER_PATH}. Preprocessing will use raw numeric values.")
    mock_logger_warning.assert_any_call(f"⚠️ Keras model not found at {model_service.MODEL_PATH}. Fallback predictor will be used.")

    # Assert that the fallback logic (worst score) was used
    assert top_kp == 2

def test_fallback_with_no_history_returns_default_kp():
    """
    Tests that the fallback returns a default KP when there's no history.
    """
    top_kp, _, _ = model_service._fallback_predictor([])
    assert top_kp == model_service.DEFAULT_KP_ID

def test_fallback_calculates_worst_average_score():
    """
    Tests the core logic of the fallback predictor.
    """
    history = [
        {"kp_id": 1, "score": 1.0, "type": "quiz"},
        {"kp_id": 1, "score": 0.8, "type": "quiz"},  # avg: 0.9
        {"kp_id": 2, "score": 0.5, "type": "quiz"},
        {"kp_id": 2, "score": 0.7, "type": "quiz"},  # avg: 0.6
        {"kp_id": 3, "score": 0.9, "type": "quiz"},
        {"kp_id": 3, "score": 0.8, "type": "quiz"},  # avg: 0.85
    ]

    top_kp, _, _ = model_service._fallback_predictor(history)

    assert top_kp == 2 # KP 2 has the lowest average score

def test_full_service_uses_fallback_if_metadata_is_missing(mocker):
    """
    If metadata is gone, the whole prediction service should use the fallback.
    """
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    mock_logger_error = mocker.patch("app.model_service.logger.error")

    history = [{"kp_id": 1, "score": 0.1, "type": "quiz"}]
    top_kp, _, _ = model_service.predict_weakest_kp(history)

    mock_logger_error.assert_called_with(f"CRITICAL: Model metadata not found at {model_service.METADATA_PATH}. Cannot proceed.")
    assert top_kp == 1
