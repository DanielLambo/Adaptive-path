# app/model_service.py
import numpy as np
from tensorflow.keras.models import load_model

# Load model once on startup
MODEL_PATH = "models/unit4_lstm.h5"
lstm_model = load_model(MODEL_PATH)

def preprocess_sequence(seq):
    """
    Pad/reshape sequence before feeding to model.
    TODO: adjust to match your Colab preprocessing.
    """
    seq = np.array(seq).reshape(1, -1, 1)  # Example: batch=1, timesteps=N, features=1
    return seq

def predict_weakest_kp(sequence):
    """
    Run LSTM prediction on a student sequence.
    Returns (weakest_kp, confidence).
    """
    x = preprocess_sequence(sequence)
    probs = lstm_model.predict(x)[0]  # first batch element
    weakest_kp = int(np.argmax(probs)) + 1   # +1 if KPs start from 1
    confidence = float(np.max(probs))
    return weakest_kp, confidence
