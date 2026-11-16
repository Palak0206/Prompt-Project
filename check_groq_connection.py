
from app.services.groq_service import generate_timetable_response


prompt = """
Return a JSON object with exactly these two fields:
"status" and "message".

Set status to "success".
Set message to "Groq connection is working".
Return JSON only.
"""


try:
    response = generate_timetable_response(prompt)

    print("\nGroq API Response:")
    print(response)

except Exception as error:
    print("\nGroq API connection failed:")
    print(type(error).__name__, error)
