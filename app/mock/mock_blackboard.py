# app/mock/mock_blackboard.py
"""
Mock Blackboard content and history API for local testing.
Replace with real Blackboard Learn API calls when access is available.

Changes made:
- Added `get_student_history` with mock data for two students.
- Added a `metadata` field to the content items.
- Added a `generate_fake_content` helper to create mock content on the fly.
- Ensured functions are deterministic by using a seed where applicable.
"""

from typing import List, Dict, Optional
from faker import Faker

# Initialize Faker for generating realistic-looking text
fake = Faker()

# --- Mock Course Content ---
# Linked to Knowledge Points (kp_id)
MOCK_CONTENT: List[Dict] = [
    # KP 1: Variables & Data Types
    {"id": "vid-101", "type": "video", "title": "Intro to Variables", "url": "https://example.com/vid-101", "kp_id": 1, "est_minutes": 6, "difficulty": 1, "metadata": {"source": "internal"}},
    {"id": "quiz-101", "type": "quiz", "title": "Variables Practice Quiz", "url": "https://example.com/quiz-101", "kp_id": 1, "est_minutes": 8, "difficulty": 1, "metadata": {}},
    # KP 2: Control Structures
    {"id": "vid-201", "type": "video", "title": "If/Else Explained", "url": "https://example.com/vid-201", "kp_id": 2, "est_minutes": 7, "difficulty": 1, "metadata": {"source": "youtube"}},
    {"id": "quiz-201", "type": "quiz", "title": "Conditional Logic Quiz", "url": "https://example.com/quiz-201", "kp_id": 2, "est_minutes": 10, "difficulty": 2, "metadata": {}},
    # KP 3: Loops
    {"id": "vid-301", "type": "video", "title": "Loops Deep Dive", "url": "https://example.com/vid-301", "kp_id": 3, "est_minutes": 12, "difficulty": 2, "metadata": {"source": "vimeo"}},
    {"id": "quiz-301", "type": "quiz", "title": "Loops Checkpoint", "url": "https://example.com/quiz-301", "kp_id": 3, "est_minutes": 10, "difficulty": 2, "metadata": {}},
    # KP 4: Functions
    {"id": "vid-401", "type": "video", "title": "Functions in Python", "url": "https://example.com/vid-401", "kp_id": 4, "est_minutes": 9, "difficulty": 2, "metadata": {}},
    {"id": "quiz-401", "type": "quiz", "title": "Functions Quiz", "url": "https://example.com/quiz-401", "kp_id": 4, "est_minutes": 11, "difficulty": 3, "metadata": {}},
]

# --- Mock Student History ---
# Schema should match what the model's preprocessing step expects.
MOCK_STUDENT_HISTORY: Dict[str, List[Dict]] = {
    "student-123": [
        {"kp_id": 1, "score": 0.9, "type": "quiz", "est_minutes": 8, "difficulty": 1},
        {"kp_id": 2, "score": 0.7, "type": "quiz", "est_minutes": 10, "difficulty": 2},
        {"kp_id": 3, "score": 0.5, "type": "quiz", "est_minutes": 10, "difficulty": 2},
    ],
    "student-456": [
        {"kp_id": 1, "score": 1.0, "type": "quiz", "est_minutes": 8, "difficulty": 1},
        {"kp_id": 4, "score": 0.6, "type": "quiz", "est_minutes": 11, "difficulty": 3},
    ],
    "student-new": [],
}


def get_content_for_kp(kp_id: int) -> List[Dict]:
    """Return all mock content linked to a given Knowledge Point ID."""
    return [c for c in MOCK_CONTENT if c["kp_id"] == kp_id]


def get_student_history(student_id: str) -> List[Dict]:
    """Return the interaction history for a given student ID."""
    return MOCK_STUDENT_HISTORY.get(student_id, [])


def generate_fake_content(
    kp_id: int, num_items: int = 3, seed: Optional[int] = None
) -> List[Dict]:
    """
    Generates a list of fake content items for a given KP.
    This is useful for testing the path builder with KPs that have no mock content.
    """
    if seed:
        Faker.seed(seed)

    content_types = ["video", "reading", "quiz", "practice"]
    items = []
    for i in range(num_items):
        content_type = content_types[i % len(content_types)]
        items.append({
            "id": f"fake-{kp_id}-{i}",
            "type": content_type,
            "title": fake.catch_phrase(),
            "url": fake.url(),
            "kp_id": kp_id,
            "est_minutes": fake.random_int(min=5, max=15),
            "difficulty": fake.random_int(min=1, max=3),
            "metadata": {"generated": True},
        })
    return items
