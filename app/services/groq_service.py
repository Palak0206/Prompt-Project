
import os

from dotenv import load_dotenv
from groq import Groq


# Load environment variables from .env
load_dotenv()


def generate_timetable_response(prompt: str) -> str:

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Send prompt to Groq
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert academic study planner. "
                    "Follow the user's instructions carefully "
                    "and return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_completion_tokens=4000
    )

    # Extract generated text
    generated_text = response.choices[0].message.content

    if not generated_text:
        raise ValueError("Groq returned an empty response.")

    return generated_text
