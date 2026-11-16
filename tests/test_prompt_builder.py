
from app.models.input_models import StudentInput
from app.services.prompt_builder import build_timetable_prompt


def test_prompt_contains_student_information():

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
            },
            {
                "name": "DBMS",
                "exam_date": "2026-11-22",
                "difficulty": "medium",
                "preparation_percentage": 60,
                "topics": []
            }
        ]
    )

    prompt = build_timetable_prompt(student)

    assert "Mathematics" in prompt
    assert "DBMS" in prompt
    assert "Integration" in prompt
    assert "2026-11-20" in prompt
    assert "2026-11-22" in prompt
    assert "max_daily_hours" in prompt


def test_prompt_contains_output_requirements():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=4,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-20",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    prompt = build_timetable_prompt(student)

    assert "Return ONLY valid JSON" in prompt
    assert '"schema_version": "1.0"' in prompt
    assert "learning" in prompt
    assert "practice" in prompt
    assert "revision" in prompt
    assert "mock_test" in prompt
