# app/models.py
"""
Pydantic Models for API Requests and Responses

This module defines the data structures used for API communication,
ensuring that all inputs and outputs are well-typed and validated.

Changes made:
- Replaced old models with a new set that aligns with the refactored services.
- Added detailed request/response models for prediction and path generation.
- Included example schemas for better OpenAPI documentation.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- Content Models ---


class ContentItem(BaseModel):
    id: str
    type: str
    title: str
    url: str
    est_minutes: int
    difficulty: int
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "vid-101",
                "type": "video",
                "title": "Intro to Variables",
                "url": "https://example.com/content/vid-101",
                "est_minutes": 6,
                "difficulty": 1,
                "metadata": {"source": "youtube"},
            }
        }


class LearningPathComponent(BaseModel):
    kp_id: int
    kp_name: str
    content: List[ContentItem]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "kp_id": 1,
                "kp_name": "Variables",
                "content": [
                    {
                        "id": "vid-101",
                        "type": "video",
                        "title": "Intro to Variables",
                        "url": "https://example.com/content/vid-101",
                        "est_minutes": 6,
                        "difficulty": 1,
                        "metadata": {"source": "youtube"},
                    }
                ],
            }
        }


# --- Prediction & Path Generation Models ---


class GeneratePathRequest(BaseModel):
    student_id: str
    # Providing history is optional. If not provided, a default path may be suggested.
    history: Optional[List[Dict[str, Any]]] = None
    # Allow forcing a path for a specific KP, bypassing prediction.
    force_kp_id: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "student_id": "student-123",
                "history": [
                    {"kp_id": 1, "score": 0.8, "type": "quiz"},
                    {"kp_id": 2, "score": 0.6, "type": "quiz"},
                ],
                "force_kp_id": None,
            }
        }


class PredictionInfo(BaseModel):
    kp_id: int
    confidence: float
    top3: List[Dict[str, Any]]


class GeneratePathResponse(BaseModel):
    student_id: str
    prediction_info: Optional[PredictionInfo] = None
    learning_path: List[LearningPathComponent]
    message: str

    class Config:
        schema_extra = {
            "example": {
                "student_id": "student-123",
                "prediction_info": {
                    "kp_id": 3,
                    "confidence": 0.85,
                    "top3": [
                        {"kp_id": 3, "confidence": 0.85},
                        {"kp_id": 5, "confidence": 0.10},
                    ],
                },
                "learning_path": [
                    # ... LearningPathComponent examples ...
                ],
                "message": "Learning path generated for weakest KP.",
            }
        }
