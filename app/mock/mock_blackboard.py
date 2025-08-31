# mock_blackboard.py
"""
Mock Blackboard content API for local testing.
Replace with real Blackboard Learn API calls when access is available.
"""

from typing import List, Dict

# Mock course content linked to Knowledge Points (kp_id)
MOCK_CONTENT: List[Dict] = [
    # Unit 4: Variables & Data Types
    {
        "id": "vid-101",
        "type": "video",
        "title": "Intro to Variables",
        "url": "https://example.com/content/vid-101",
        "kp_id": 1,
        "est_minutes": 6,
        "difficulty": 1,
    },
    {
        "id": "quiz-101",
        "type": "quiz",
        "title": "Variables Practice Quiz",
        "url": "https://example.com/content/quiz-101",
        "kp_id": 1,
        "est_minutes": 8,
        "difficulty": 1,
    },

    # Control Structures
    {
        "id": "vid-201",
        "type": "video",
        "title": "If/Else Explained",
        "url": "https://example.com/content/vid-201",
        "kp_id": 2,
        "est_minutes": 7,
        "difficulty": 1,
    },
    {
        "id": "quiz-201",
        "type": "quiz",
        "title": "Conditional Logic Quiz",
        "url": "https://example.com/content/quiz-201",
        "kp_id": 2,
        "est_minutes": 10,
        "difficulty": 1,
    },

    # Loops
    {
        "id": "vid-301",
        "type": "video",
        "title": "Loops Deep Dive",
        "url": "https://example.com/content/vid-301",
        "kp_id": 3,
        "est_minutes": 12,
        "difficulty": 2,
    },
    {
        "id": "quiz-301",
        "type": "quiz",
        "title": "Loops Checkpoint",
        "url": "https://example.com/content/quiz-301",
        "kp_id": 3,
        "est_minutes": 10,
        "difficulty": 2,
    },

    # Functions
    {
        "id": "vid-401",
        "type": "video",
        "title": "Functions in Python",
        "url": "https://example.com/content/vid-401",
        "kp_id": 4,
        "est_minutes": 9,
        "difficulty": 2,
    },
    {
        "id": "quiz-401",
        "type": "quiz",
        "title": "Functions Quiz",
        "url": "https://example.com/content/quiz-401",
        "kp_id": 4,
        "est_minutes": 11,
        "difficulty": 2,
    },

    # Lists & Dictionaries
    {
        "id": "vid-501",
        "type": "video",
        "title": "Lists & Dictionaries",
        "url": "https://example.com/content/vid-501",
        "kp_id": 5,
        "est_minutes": 8,
        "difficulty": 2,
    },
    {
        "id": "quiz-501",
        "type": "quiz",
        "title": "Data Structures Quiz",
        "url": "https://example.com/content/quiz-501",
        "kp_id": 5,
        "est_minutes": 12,
        "difficulty": 2,
    },

    # Recursion
    {
        "id": "vid-601",
        "type": "video",
        "title": "Recursion Explained",
        "url": "https://example.com/content/vid-601",
        "kp_id": 6,
        "est_minutes": 14,
        "difficulty": 3,
    },
    {
        "id": "quiz-601",
        "type": "quiz",
        "title": "Recursion Practice Quiz",
        "url": "https://example.com/content/quiz-601",
        "kp_id": 6,
        "est_minutes": 12,
        "difficulty": 3,
    },

    # Object-Oriented Programming
    {
        "id": "vid-701",
        "type": "video",
        "title": "OOP Basics",
        "url": "https://example.com/content/vid-701",
        "kp_id": 7,
        "est_minutes": 15,
        "difficulty": 3,
    },
    {
        "id": "quiz-701",
        "type": "quiz",
        "title": "OOP Quiz",
        "url": "https://example.com/content/quiz-701",
        "kp_id": 7,
        "est_minutes": 14,
        "difficulty": 3,
    },

    # File Handling
    {
        "id": "vid-801",
        "type": "video",
        "title": "File Handling in Python",
        "url": "https://example.com/content/vid-801",
        "kp_id": 8,
        "est_minutes": 9,
        "difficulty": 2,
    },
    {
        "id": "quiz-801",
        "type": "quiz",
        "title": "File Handling Quiz",
        "url": "https://example.com/content/quiz-801",
        "kp_id": 8,
        "est_minutes": 10,
        "difficulty": 2,
    },
]


def get_content_for_kp(kp_id: int) -> List[Dict]:
    """Return all mock content linked to a given Knowledge Point ID."""
    return [c for c in MOCK_CONTENT if c["kp_id"] == kp_id]
