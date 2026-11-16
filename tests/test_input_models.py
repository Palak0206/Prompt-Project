
from app.models.input_models import StudentInput


def test_valid_student_input():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=4,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-20",
                "difficulty": "hard",
                "preparation_percentage": 40,
                "topics": ["Integration", "Matrices"]
            }
        ]
    )

    assert student.subjects[0].name == "Mathematics"
    assert student.subjects[0].preparation_percentage == 40
    assert student.preferences.max_session_duration_minutes == 90

import pytest
from pydantic import ValidationError
from app.models.input_models import StudentInput


def test_invalid_preparation_percentage():

    with pytest.raises(ValidationError):

        StudentInput(
            start_date="2026-11-16",
            max_daily_hours=4,
            subjects=[
                {
                    "name": "Mathematics",
                    "exam_date": "2026-11-20",
                    "difficulty": "hard",
                    "preparation_percentage": 120,
                    "topics": []
                }
            ]
        )


def test_duplicate_subject_names():

    with pytest.raises(ValidationError):

        StudentInput(
            start_date="2026-11-16",
            max_daily_hours=4,
            subjects=[
                {
                    "name": "Mathematics",
                    "exam_date": "2026-11-20",
                    "difficulty": "hard",
                    "preparation_percentage": 40
                },
                {
                    "name": "mathematics",
                    "exam_date": "2026-11-22",
                    "difficulty": "easy",
                    "preparation_percentage": 70
                }
            ]
        )
