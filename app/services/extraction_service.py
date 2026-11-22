
import os
import json

from datetime import date
from dotenv import load_dotenv
from groq import Groq

from app.models.extraction_schema import STUDENT_EXTRACTION_SCHEMA


load_dotenv()


def extract_student_details(query: str) -> dict:

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    client = Groq(api_key=api_key)

    system_prompt = f"""
    You are an expert student information extraction assistant.

    Your task is to extract study planning information from the
    student's natural language description.

    Today's date is {date.today().isoformat()}.

    Extract the following information:
    - Study plan start date
    - Maximum daily study hours
    - Subject names
    - Exam dates
    - Subject difficulty
    - Preparation percentage
    - Topics for each subject
    - Maximum study session duration

    IMPORTANT RULES:

    1. Do not invent information that the student has not provided.
    2. If a required detail is missing, return null.
    3. If the student provides a relative date such as tomorrow,
       resolve it using today's date.
    4. Convert all dates into YYYY-MM-DD format.
    5. Difficulty must be easy, medium, or hard.
    6. Preparation percentage must be an integer between 0 and 100.
    7. If no topics are provided for a subject, return an empty list.
    8. If maximum session duration is not specified, return null.
    9. Extract every subject mentioned by the student.
    10. Do not generate a timetable.
    11. Do not add explanations or extra fields.
    12. Follow the provided JSON schema exactly.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "student_extraction",
                "strict": True,
                "schema": STUDENT_EXTRACTION_SCHEMA
            }
        },
        temperature=0.1,
        max_completion_tokens=3000
    )

    generated_text = response.choices[0].message.content

    if not generated_text:
        raise ValueError("Groq returned an empty extraction response.")

    return json.loads(generated_text)
