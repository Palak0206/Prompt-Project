
from app import create_app
from unittest.mock import patch
from app.services.timetable_service import TimetableGenerationError


def test_validate_input_success():

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/validate-input",
        json={
            "start_date": "2026-11-16",
            "max_daily_hours": 4,
            "subjects": [
                {
                    "name": "Mathematics",
                    "exam_date": "2026-11-20",
                    "difficulty": "hard",
                    "preparation_percentage": 40,
                    "topics": ["Integration"]
                }
            ]
        }
    )

    assert response.status_code == 200
    assert response.json["message"] == "Student input is valid."


def test_validate_input_failure():

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/validate-input",
        json={
            "start_date": "2026-11-16",
            "max_daily_hours": 4,
            "subjects": [
                {
                    "name": "Mathematics",
                    "exam_date": "2026-11-20",
                    "difficulty": "impossible",
                    "preparation_percentage": 40
                }
            ]
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Input validation failed."

def test_preview_prompt_success():

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/preview-prompt",
        json={
            "start_date": "2026-11-16",
            "max_daily_hours": 4,
            "subjects": [
                {
                    "name": "Mathematics",
                    "exam_date": "2026-11-20",
                    "difficulty": "hard",
                    "preparation_percentage": 40,
                    "topics": ["Integration"]
                }
            ]
        }
    )

    assert response.status_code == 200
    assert response.json["message"] == "Prompt generated successfully."
    assert "Mathematics" in response.json["prompt"]


def test_preview_prompt_invalid_input():

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/preview-prompt",
        json={
            "start_date": "2026-11-16",
            "max_daily_hours": 4,
            "subjects": []
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Input validation failed."

def test_generate_timetable_success():

    app = create_app()
    client = app.test_client()

    mock_timetable = {
        "schema_version": "1.0",
        "days": [
            {
                "date": "2026-11-16",
                "items": []
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

    with patch(
        "app.routes.generate_timetable"
    ) as mock_generator:

        mock_generator.return_value.model_dump.return_value = mock_timetable

        response = client.post(
            "/api/generate-timetable",
            json={
                "start_date": "2026-11-16",
                "max_daily_hours": 4,
                "subjects": [
                    {
                        "name": "Mathematics",
                        "exam_date": "2026-11-18",
                        "difficulty": "hard",
                        "preparation_percentage": 40,
                        "topics": []
                    }
                ]
            }
        )

    assert response.status_code == 200
    assert response.json["message"] == "Timetable generated successfully."
    assert len(response.json["timetable"]["days"]) == 3


def test_generate_timetable_invalid_input():

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/generate-timetable",
        json={
            "start_date": "2026-11-16",
            "max_daily_hours": 4,
            "subjects": []
        }
    )

    assert response.status_code == 400


def test_generate_timetable_generation_failure():

    app = create_app()
    client = app.test_client()

    with patch(
        "app.routes.generate_timetable",
        side_effect=TimetableGenerationError("Invalid generated timetable.")
    ):

        response = client.post(
            "/api/generate-timetable",
            json={
                "start_date": "2026-11-16",
                "max_daily_hours": 4,
                "subjects": [
                    {
                        "name": "Mathematics",
                        "exam_date": "2026-11-18",
                        "difficulty": "hard",
                        "preparation_percentage": 40
                    }
                ]
            }
        )

    assert response.status_code == 422
    assert response.json["error"] == "Timetable generation failed."
