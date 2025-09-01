# tests/test_mock_blackboard.py
import pytest
from app.mock.mock_blackboard import (
    get_content_for_kp,
    get_student_history,
    generate_fake_content,
    MOCK_CONTENT,
)

def test_get_content_for_kp_returns_correct_items():
    """
    Tests that get_content_for_kp returns all and only the correct items.
    """
    kp_id = 1
    content = get_content_for_kp(kp_id)

    # Check that we got the right number of items
    expected_count = sum(1 for item in MOCK_CONTENT if item["kp_id"] == kp_id)
    assert len(content) == expected_count

    # Check that all returned items have the correct kp_id
    for item in content:
        assert item["kp_id"] == kp_id
        assert "title" in item
        assert "type" in item

def test_get_content_for_nonexistent_kp_returns_empty():
    """
    Tests that get_content_for_kp returns an empty list for a KP with no content.
    """
    assert get_content_for_kp(999) == []

def test_get_student_history_known_student():
    """
    Tests fetching history for a student who exists in the mock data.
    """
    history = get_student_history("student-123")
    assert isinstance(history, list)
    assert len(history) > 0
    assert "kp_id" in history[0]
    assert "score" in history[0]

def test_get_student_history_unknown_student():
    """
    Tests that an empty list is returned for a student not in the mock data.
    """
    assert get_student_history("unknown-student") == []

def test_generate_fake_content_creates_correct_number():
    """
    Tests that the generator creates the requested number of items.
    """
    num_items = 5
    generated_content = generate_fake_content(kp_id=10, num_items=num_items)
    assert len(generated_content) == num_items
    for item in generated_content:
        assert item["kp_id"] == 10
        assert "title" in item

def test_generate_fake_content_is_deterministic_with_seed():
    """
    Tests that with the same seed, the generated content is identical.
    """
    content1 = generate_fake_content(kp_id=20, num_items=3, seed=42)
    content2 = generate_fake_content(kp_id=20, num_items=3, seed=42)
    assert content1 == content2

    # And different with a different seed
    content3 = generate_fake_content(kp_id=20, num_items=3, seed=43)
    assert content1 != content3
