import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Force TensorFlow CPU only (avoid GPU thread issues on macOS)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

MODEL_PATH = "models/best_model.h5"
SCALER_PATH = "models/feature_scaler.pkl"

# Globals, will be initialized lazily
lstm_model = None
feature_scaler = None

# Must match Colab training config
MAX_SEQ_LEN = 50
NUM_FEATURES = 10

CATEGORICAL_FEATURES = [
    "year_Freshman", "year_Sophomore", "year_Junior", "year_Senior",
    "major_CS", "major_EE", "major_ME",
    "assessment_type_quiz", "assessment_type_exam"
]
NUMERIC_FEATURES = ["score", "avg_difficulty", "days_since_start"]

def load_services():
    """Lazy-load model and scaler so Uvicorn doesn't crash at startup."""
    global lstm_model, feature_scaler
    if lstm_model is None:
        lstm_model = load_model(MODEL_PATH)
        print("✅ Model loaded")
    if feature_scaler is None:
        try:
            feature_scaler = joblib.load(SCALER_PATH)
            print("✅ Feature scaler loaded")
        except Exception as e:
            print(f"⚠️ No scaler found, using raw values. {e}")
            feature_scaler = None

def preprocess_sequence(raw_sequence: list[dict]) -> np.ndarray:
    """Convert raw history into model-ready padded sequence."""
    load_services()  # ensure model + scaler are ready

    seq_matrix = []
    for timestep in raw_sequence:
        row = []

        # Numeric features
        nums = [timestep[f] for f in NUMERIC_FEATURES]
        if feature_scaler:
            nums = feature_scaler.transform([nums])[0]
        row.extend(nums)

        # One-hot categorical
        for cat in CATEGORICAL_FEATURES:
            base, val = cat.split("_", 1)
            row.append(1 if timestep.get(base) == val else 0)

        seq_matrix.append(row)

    seq_matrix = np.array(seq_matrix, dtype="float32")
    padded = pad_sequences([seq_matrix], maxlen=MAX_SEQ_LEN, dtype="float32", padding="pre")[0]

    return padded.reshape(1, MAX_SEQ_LEN, len(seq_matrix[0]))

def predict_weakest_kp(raw_sequence: list[dict]) -> tuple[int, float]:
    """Predict weakest KP with confidence score."""
    load_services()
    x = preprocess_sequence(raw_sequence)
    probs = lstm_model.predict(x, verbose=0)[0]

    weakest_kp = int(np.argmax(probs)) + 1  # assumes kp_id starts at 1
    confidence = float(np.max(probs))
    return weakest_kp, confidence
