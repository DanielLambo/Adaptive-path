# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from app.model_service import predict_weakest_kp
from app.path_builder import build_learning_path

app = FastAPI()

class SequenceRequest(BaseModel):
    student_id: int
    sequence: list[int]   # student activity/performance sequence

@app.post("/predict")
async def predict(req: SequenceRequest):
    weakest_kp, confidence = predict_weakest_kp(req.sequence)
    path = await build_learning_path(weakest_kp)
    return {
        "student_id": req.student_id,
        "weakest_kp": weakest_kp,
        "confidence": confidence,
        "learning_path": path,
    }
