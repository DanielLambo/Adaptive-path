import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Force TensorFlow to run on CPU (no GPU stress)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# -----------------------------
# Model & Scaler Setup
# -----------------------------
MODEL_PATH = "models/best_model.h5"
SCALER_PATH = "models/feature_scaler.pkl"

# Load trained model
lstm_model = load_model(MODEL_PATH)

# Try to load scaler (exported from Colab)
try:
    feature_scaler = joblib.load(SCALER_PATH)
    print("✅ Feature scaler loaded successfully.")
except Exception as e:
    feature_scaler = None
    print(f"⚠️ No scaler found. Using raw numeric features. Error: {e}")

# -----------------------------
# Preprocessing Configuration
# -----------------------------
# Must match values from Colab
MAX_SEQ_LEN = 50        # replace with actual max_seq_length used
NUM_FEATURES = 10       # replace with len(sequence_features) from Colab

# List of categorical one-hot features (match your Colab dataset)
CATEGORICAL_FEATURES = [
    "year_Freshman", "year_Sophomore", "year_Junior", "year_Senior",
    "major_CS", "major_EE", "major_ME",
    "assessment_type_quiz", "assessment_type_exam"
]

NUMERIC_FEATURES = ["score", "avg_difficulty", "days_since_start"]

# -----------------------------
# Preprocessing Function
# -----------------------------
def preprocess_sequence(raw_sequence: list[dict]) -> np.ndarray:
    """
    Convert a student's activity history into a model-ready padded sequence.
    
    raw_sequence: list of dicts with keys:
        score, avg_difficulty, days_since_start, year, major, assessment_type
    
    Returns: np.ndarray of shape (1, MAX_SEQ_LEN, NUM_FEATURES)
    """
    seq_matrix = []

    for timestep in raw_sequence:
        row = []

        # --- Numeric features (scaled) ---
        nums = [timestep[f] for f in NUMERIC_FEATURES]
        if feature_scaler:
            nums = feature_scaler.transform([nums])[0]
        row.extend(nums)

        # --- One-hot categorical features ---
        for cat in CATEGORICAL_FEATURES:
            base, val = cat.split("_", 1)
            row.append(1 if timestep.get(base) == val else 0)

        seq_matrix.append(row)

    seq_matrix = np.array(seq_matrix, dtype="float32")

    # Pad sequence to fixed length
    padded = pad_sequences([seq_matrix], maxlen=MAX_SEQ_LEN, dtype="float32", padding="pre")[0]

    return padded.reshape(1, MAX_SEQ_LEN, len(seq_matrix[0]))

# -----------------------------
# Prediction Function
# -----------------------------
def predict_weakest_kp(raw_sequence: list[dict]) -> tuple[int, float]:
    """
    Predict the weakest knowledge point for a student.
    
    raw_sequence: list of dicts (student's learning history).
    Returns: (weakest_kp_id, confidence_score)
    """
    x = preprocess_sequence(raw_sequence)
    probs = lstm_model.predict(x, verbose=0)[0]

    weakest_kp = int(np.argmax(probs)) + 1   # assumes kp_id starts at 1
    confidence = float(np.max(probs))

    return weakest_kp, confidence
