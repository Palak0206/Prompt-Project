
from unittest.mock import patch

import pytest

from app.models.input_models import StudentInput
from app.services.timetable_service import (
    generate_timetable,
    TimetableGenerationError
)


def create_student():

    return StudentInput(
        start_date="2026-11-16",
        max_daily_hours=2,
        subjects=[
            {
                "name": "Mathematics",
                "exam_date": "2026-11-18",
                "difficulty": "hard",
                "preparation_percentage": 40,
                "topics": ["Integration"]
            }
        ]
    )


def test_successful_timetable_generation():

    student = create_student()

    mock_response = """
    {
        "schema_version": "1.0",
        "days": [
            {
                "date": "2026-11-16",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "learning",
                        "task": "Understand integration",
                        "topics": ["Integration"],
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
    }
    """

    with patch(
        "app.services.timetable_service.build_timetable_prompt"
    ) as mock_builder:

        with patch(
            "app.services.timetable_service.generate_timetable_response"
        ) as mock_groq:

            mock_builder.return_value = "Test prompt"
            mock_groq.return_value = mock_response

            result = generate_timetable(student)

    assert result.schema_version == "1.0"
    assert len(result.days) == 3
    assert result.days[0].items[0].subject == "Mathematics"

    mock_builder.assert_called_once_with(student)
    mock_groq.assert_called_once_with("Test prompt")

def test_invalid_json_response():

    student = create_student()

    with patch(
        "app.services.timetable_service.build_timetable_prompt",
        return_value="Test prompt"
    ):

        with patch(
            "app.services.timetable_service.generate_timetable_response",
            side_effect=[
                "Not valid JSON",
                "Still not valid JSON"
            ]
        ) as mock_groq:

            with pytest.raises(
                TimetableGenerationError,
                match="invalid JSON"
            ):
                generate_timetable(student)

    assert mock_groq.call_count == 2


def test_invalid_output_structure():

    student = create_student()

    invalid_response = """
    {
        "schema_version": "2.0",
        "days": []
    }
    """

    with patch(
        "app.services.timetable_service.build_timetable_prompt",
        return_value="Test prompt"
    ):

        with patch(
            "app.services.timetable_service.generate_timetable_response",
            return_value=invalid_response
        ) as mock_groq:

            with pytest.raises(
                TimetableGenerationError,
                match="Invalid timetable structure"
            ):
                generate_timetable(student)

    assert mock_groq.call_count == 2


def test_timetable_violating_exam_date_rule():

    student = create_student()

    invalid_timetable = """
    {
        "schema_version": "1.0",
        "days": [
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {
                "date": "2026-11-18",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "revision",
                        "task": "Revise integration",
                        "topics": ["Integration"],
                        "duration_minutes": 30
                    }
                ]
            }
        ]
    }
    """

    with patch(
        "app.services.timetable_service.build_timetable_prompt",
        return_value="Test prompt"
    ):

        with patch(
            "app.services.timetable_service.generate_timetable_response",
            return_value=invalid_timetable
        ) as mock_groq:

            with pytest.raises(
                TimetableGenerationError,
                match="remained invalid after 2 attempts"
            ):
                generate_timetable(student)

    assert mock_groq.call_count == 2

def test_invalid_timetable_corrected_on_retry():

    student = create_student()

    invalid_response = """
    {
        "schema_version": "1.0",
        "days": [
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {
                "date": "2026-11-18",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "revision",
                        "task": "Revise integration",
                        "topics": ["Integration"],
                        "duration_minutes": 30
                    }
                ]
            }
        ]
    }
    """

    valid_response = """
    {
        "schema_version": "1.0",
        "days": [
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {"date": "2026-11-18", "items": []}
        ]
    }
    """

    with patch(
        "app.services.timetable_service.build_timetable_prompt",
        return_value="Original prompt"
    ):

        with patch(
            "app.services.timetable_service.generate_timetable_response",
            side_effect=[invalid_response, valid_response]
        ) as mock_groq:

            result = generate_timetable(student)

    assert result.schema_version == "1.0"
    assert len(result.days) == 3

    assert mock_groq.call_count == 2

    # Verify that the second request contains correction instructions
    second_prompt = mock_groq.call_args_list[1].args[0]

    assert "CORRECTION REQUEST" in second_prompt
    assert "on or after its exam date" in second_prompt

def test_invalid_timetable_corrected_on_retry():

    student = create_student()

    invalid_response = """
    {
        "schema_version": "1.0",
        "days": [
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {
                "date": "2026-11-18",
                "items": [
                    {
                        "kind": "session",
                        "subject": "Mathematics",
                        "session_type": "revision",
                        "task": "Revise integration",
                        "topics": ["Integration"],
                        "duration_minutes": 30
                    }
                ]
            }
        ]
    }
    """

    valid_response = """
    {
        "schema_version": "1.0",
        "days": [
            {"date": "2026-11-16", "items": []},
            {"date": "2026-11-17", "items": []},
            {"date": "2026-11-18", "items": []}
        ]
    }
    """

    with patch(
        "app.services.timetable_service.build_timetable_prompt",
        return_value="Original prompt"
    ):

        with patch(
            "app.services.timetable_service.generate_timetable_response",
            side_effect=[invalid_response, valid_response]
        ) as mock_groq:

            result = generate_timetable(student)

    assert result.schema_version == "1.0"
    assert len(result.days) == 3

    assert mock_groq.call_count == 2

    # Verify that the second request contains correction instructions
    second_prompt = mock_groq.call_args_list[1].args[0]

    assert "CORRECTION REQUEST" in second_prompt
    assert "on or after its exam date" in second_prompt


