# app/model_service.py
"""
Model Serving and Preprocessing Service

This module is responsible for loading the ML model and feature scaler,
preprocessing input data, and making predictions.

Changes made:
- Implemented strict lazy-loading for TensorFlow and joblib to prevent
  import-time crashes, especially on macOS.
- Services (model, scaler, metadata) are now loaded only once when first needed.
- Added a robust fallback predictor that activates if model/scaler files are missing.
  It uses a deterministic rule (worst average score).
- All configuration (sequence length, feature names) is now loaded from
  `models/metadata.json` instead of being hardcoded.
- The preprocessing pipeline was updated to match the metadata configuration,
  ensuring parity with the training environment.
- The prediction function now returns the top 3 recommendations with confidence.
"""
import os
import json
import numpy as np
import logging
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Set up a logger for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths to model artifacts
MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "best_model.h5")
SCALER_PATH = os.path.join(MODELS_DIR, "feature_scaler.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "metadata.json")
DEFAULT_KP_ID = 1  # Fallback KP if no history and no model

# --- Service State ---
# A dictionary to hold the loaded services (model, scaler, metadata)
_services: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "metadata": None,
    "loaded": False,
}


def load_services():
    """
    Lazy-loads all services: metadata, feature scaler, and the Keras model.
    This function is designed to be called only once.
    """
    if _services["loaded"]:
        return

    logger.info("Attempting to load ML services...")

    # 1. Load Metadata (required)
    try:
        with open(METADATA_PATH, "r") as f:
            _services["metadata"] = json.load(f)
        logger.info("✅ Model metadata loaded successfully.")
    except FileNotFoundError:
        logger.error(
            f"CRITICAL: Model metadata not found at {METADATA_PATH}. Cannot proceed."
        )
        # Mark as loaded to prevent retries, but services will be None
        _services["loaded"] = True
        return

    # 2. Load Feature Scaler (optional, fallback available)
    try:
        import joblib

        _services["scaler"] = joblib.load(SCALER_PATH)
        logger.info("✅ Feature scaler loaded successfully.")
    except FileNotFoundError:
        logger.warning(
            f"⚠️ Feature scaler not found at {SCALER_PATH}. Preprocessing will use raw numeric values."
        )
    except Exception as e:
        logger.error(f"❌ Error loading feature scaler: {e}")

    # 3. Load Keras Model (optional, fallback available)
    try:
        from tensorflow.keras.models import load_model

        # Suppress verbose TensorFlow logging
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        _services["model"] = load_model(MODEL_PATH)
        logger.info("✅ Keras model loaded successfully.")
    except FileNotFoundError:
        logger.warning(
            f"⚠️ Keras model not found at {MODEL_PATH}. Fallback predictor will be used."
        )
    except ImportError:
        logger.warning("⚠️ TensorFlow not installed. Fallback predictor will be used.")
    except Exception as e:
        logger.error(f"❌ Error loading Keras model: {e}")

    _services["loaded"] = True


def _fallback_predictor(
    history: List[Dict],
) -> Tuple[int, float, List[Tuple[int, float]]]:
    """
    Deterministic fallback predictor.
    - If history exists, it finds the KP with the lowest average 'score'.
    - If no history, it returns a default KP.
    """
    logger.warning("Using fallback predictor.")
    if not history:
        return DEFAULT_KP_ID, 1.0, [(DEFAULT_KP_ID, 1.0)]

    kp_scores = {}
    for item in history:
        kp_id = item.get("kp_id")
        score = item.get("score", 0)
        if kp_id is not None:
            if kp_id not in kp_scores:
                kp_scores[kp_id] = []
            kp_scores[kp_id].append(score)

    if not kp_scores:
        return DEFAULT_KP_ID, 1.0, [(DEFAULT_KP_ID, 1.0)]

    # Calculate average scores and find the KP with the minimum average
    avg_scores = {kp: np.mean(scores) for kp, scores in kp_scores.items()}
    worst_kp = min(avg_scores, key=avg_scores.get)

    # The fallback doesn't have confidence scores or a top3 list
    return worst_kp, 1.0, [(worst_kp, 1.0)]


def preprocess_sequence(raw_sequence: List[Dict], metadata: Dict) -> np.ndarray:
    """
    Converts a raw sequence of student history into a model-ready padded sequence.
    """
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    max_seq_len = metadata["max_seq_len"]
    numeric_features = metadata["numeric_features"]
    categorical_map = metadata["categorical_features_map"]
    all_features_ordered = metadata["sequence_features"]

    feature_matrix = []
    for timestep in raw_sequence:
        row = {}
        # 1. Process numeric features
        for feat in numeric_features:
            row[feat] = timestep.get(feat, 0)

        # 2. Process categorical features (one-hot encode)
        for base_feat, categories in categorical_map.items():
            for category in categories:
                col_name = f"{base_feat}_{category}"
                row[col_name] = 1 if timestep.get(base_feat) == category else 0

        # Ensure the final order is correct
        ordered_row = [row[feat] for feat in all_features_ordered]
        feature_matrix.append(ordered_row)

    # Scale numeric features if scaler is available
    if _services["scaler"]:
        numeric_indices = [all_features_ordered.index(f) for f in numeric_features]
        numeric_data = np.array(feature_matrix)[:, numeric_indices]
        scaled_numeric_data = _services["scaler"].transform(numeric_data)

        # Replace original numeric data with scaled data
        for i, idx in enumerate(numeric_indices):
            for row_idx in range(len(feature_matrix)):
                feature_matrix[row_idx][idx] = scaled_numeric_data[row_idx][i]

    # Pad the sequence
    padded = pad_sequences(
        [feature_matrix],
        maxlen=max_seq_len,
        dtype="float32",
        padding="pre",
        truncating="pre",
    )

    # Reshape for the LSTM model: (1, max_seq_len, num_features)
    return padded.reshape(1, max_seq_len, len(all_features_ordered))


def predict_weakest_kp(
    history: List[Dict],
) -> Tuple[int, float, List[Tuple[int, float]]]:
    """
    Predicts the user's weakest knowledge point based on their history.

    Returns:
        - top_kp_id (int): The ID of the most likely weakest KP.
        - confidence (float): The model's confidence in this prediction.
        - top3 (list): A list of (kp_id, probability) for the top 3 predictions.
    """
    load_services()

    # If model or metadata is not available, use the fallback
    if not _services["model"] or not _services["metadata"]:
        return _fallback_predictor(history)

    if not history:
        # Model can't predict on empty sequence, use fallback logic
        return _fallback_predictor(history)

    # Preprocess the data
    processed_input = preprocess_sequence(history, _services["metadata"])

    # Make prediction
    probs = _services["model"].predict(processed_input, verbose=0)[0]

    # Get top 3 predictions
    top3_indices = np.argsort(probs)[-3:][::-1]

    kp_labels = _services["metadata"]["kp_label_encoder"]

    # Assuming kp_ids are 1-based index from the label list
    top3_with_probs = [
        (kp_labels.index(kp_labels[i]) + 1, float(probs[i])) for i in top3_indices
    ]

    top_kp_id, confidence = top3_with_probs[0]

    return top_kp_id, confidence, top3_with_probs
