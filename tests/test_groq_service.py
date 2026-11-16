
from unittest.mock import patch, MagicMock

import pytest

from app.services.groq_service import generate_timetable_response


def test_groq_successful_response():

    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"schema_version": "1.0", "days": []}'
    )

    with patch("app.services.groq_service.Groq") as mock_groq:

        mock_client = mock_groq.return_value
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(
            "os.environ",
            {
                "GROQ_API_KEY": "test_api_key",
                "GROQ_MODEL": "openai/gpt-oss-20b"
            }
        ):

            prompt = "Generate a timetable and return JSON."

            result = generate_timetable_response(prompt)

    assert result == '{"schema_version": "1.0", "days": []}'

    mock_groq.assert_called_once_with(api_key="test_api_key")

    mock_client.chat.completions.create.assert_called_once()


def test_groq_missing_api_key():

    with patch.dict("os.environ", {}, clear=True):

        with pytest.raises(
            ValueError,
            match="GROQ_API_KEY is missing"
        ):
            generate_timetable_response("Test prompt")


def test_groq_empty_response():

    mock_response = MagicMock()
    mock_response.choices[0].message.content = None

    with patch("app.services.groq_service.Groq") as mock_groq:

        mock_client = mock_groq.return_value
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(
            "os.environ",
            {"GROQ_API_KEY": "test_api_key"}
        ):

            with pytest.raises(
                ValueError,
                match="Groq returned an empty response"
            ):
                generate_timetable_response("Test prompt")
    