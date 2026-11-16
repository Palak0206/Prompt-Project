
from app import create_app


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
