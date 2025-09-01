from pydantic import BaseModel, Field
from typing import List, Any, Dict, Optional

class GeneratePathRequest(BaseModel):
    student_id: int = Field(..., ge=1)
    override_kp_id: Optional[int] = Field(None, ge=1)

class ModuleItem(BaseModel):
    id: str
    type: str
    title: str
    url: str
    est_minutes: int
    difficulty: int

class Module(BaseModel):
    stage: str
    kp: Dict[str, Any]
    items: List[ModuleItem]

class GeneratePathResponse(BaseModel):
    goal_kp: Dict[str, Any]
    estimated_minutes: int
    modules: List[Module]
    prediction: Optional[Dict[str, Any]] = None

class ProgressEvent(BaseModel):
    student_id: int
    kp_id: int
    new_proficiency: float  # 0..1
