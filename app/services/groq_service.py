import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def generate_timetable_response(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert academic study planner. "
                    "Generate a realistic and practical study timetable. "
                    "Return only a valid JSON object. "
                    "Do not include Markdown, code fences, or explanations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        reasoning_effort="low",
        include_reasoning=False,
        temperature=0.2,
        max_completion_tokens=8000
    )

    choice = response.choices[0]
    message = choice.message

    print("Groq finish reason:", choice.finish_reason)
    print("Groq usage:", response.usage)

    generated_text = message.content

    if not generated_text:
        raise ValueError(
            f"Groq returned empty content. "
            f"Finish reason: {choice.finish_reason}. "
            f"Reasoning available: {bool(message.reasoning)}"
        )

    return generated_text.strip()