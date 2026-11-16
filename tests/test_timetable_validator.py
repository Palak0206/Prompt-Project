
from app.models.input_models import StudentInput
from app.models.output_models import TimetableOutput

from app.validators.timetable_validator import validate_timetable


def test_daily_study_limit_exceeded():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {
                "date": "2026-11-16",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "learning",
                        "task": "Study integration",
                        "duration_minutes": 90
                    },
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "practice",
                        "task": "Solve integration problems",
                        "duration_minutes": 60
                    }
                ]
            },
            {
                "date": "2026-11-17",
                "items": []
            },
            {
                "date": "2026-11-18",
                "items": []
            }
        ]
    )

    errors = validate_timetable(timetable, student)

    assert any(
        "Daily study limit exceeded" in error
        for error in errors
    )


def test_valid_timetable_has_no_errors():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {
                "date": "2026-11-16",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "learning",
                        "task": "Study integration",
                        "duration_minutes": 90
                    },
                    {
                        "kind": "break",
                        "duration_minutes": 15
                    }
                ]
            },
            {
                "date": "2026-11-17",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "revision",
                        "task": "Revise integration",
                        "duration_minutes": 60
                    }
                ]
            },
            {
                "date": "2026-11-18",
                "items": []
            }
        ]
    )

    errors = validate_timetable(timetable, student)

    assert errors == []

def test_subject_scheduled_on_exam_date():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {
                "date": "2026-11-18",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "revision",
                        "task": "Revise mathematics",
                        "duration_minutes": 30
                    }
                ]
            }
        ]
    )

    errors = validate_timetable(timetable, student)

    assert any("on or after its exam date" in error for error in errors)


def test_unknown_subject():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {
                "date": "2026-11-16",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Physics",
                        "session_type": "learning",
                        "task": "Study mechanics",
                        "duration_minutes": 30
                    }
                ]
            },
            {"date": "2026-11-17", "items": []},
            {"date": "2026-11-18", "items": []}
        ]
    )

    errors = validate_timetable(timetable, student)

    assert any("Unknown subject" in error for error in errors)


def test_missing_planning_date():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {"date": "2026-11-16", "items": []},
            # November 17 is intentionally missing
            {"date": "2026-11-18", "items": []}
        ]
    )

    errors = validate_timetable(timetable, student)

    assert any("every planning date" in error for error in errors)


def test_invalid_syllabus_topic():

    student = StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40,
                "topics": ["Integration", "Matrices"]
            }
        ]
    )

    timetable = TimetableOutput(
        schema_version="1.0",
        days=[
            {
                "date": "2026-11-16",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "learning",
                        "task": "Study algebra",
                        "topics": ["Algebra"],
                        "duration_minutes": 30
                    }
                ]
            },
            {"date": "2026-11-17", "items": []},
            {"date": "2026-11-18", "items": []}
        ]
    )

    errors = validate_timetable(timetable, student)

    assert any("Invalid topic" in error for error in errors)
