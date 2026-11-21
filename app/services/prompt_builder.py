
import json

from app.models.input_models import StudentInput


def build_timetable_prompt(student: StudentInput) -> str:

    # Convert validated student data into a JSON-compatible dictionary
    student_data = student.model_dump(mode="json")

    # Find the latest exam date
    latest_exam_date = max(
        subject.exam_date for subject in student.subjects
    )

    latest_exam_date = latest_exam_date.isoformat()

    prompt = f"""
You are an expert academic study planner.

Your task is to create a personalized study timetable
using the student's information provided below.

STUDENT INFORMATION:

{json.dumps(student_data, indent=2)}

PLANNING RULES:

1. Generate a timetable starting from the student's
   start_date through the latest exam date, inclusive.

2. Include every calendar date exactly once and in
   chronological order.

3. A subject must never be scheduled on or after its
   own exam date.

4. Never invent subjects or syllabus topics.

5. If a subject has supplied topics, use only those
   exact topic names.

6. If no topics are supplied for a subject, keep its
   topics list empty and write general study tasks.

7. The total duration of study sessions on any day
   must not exceed max_daily_hours.

8. Break durations do not count towards the daily
   study-hour limit.

9. Individual study sessions must not exceed
   max_session_duration_minutes.

10. Empty days are allowed when appropriate.

11. Use preparation percentage and difficulty to
    help decide how to distribute study effort.

12. Revision and mock tests are useful planning
    options, but do not force them for every subject.
13. Avoid scheduling the same topic for initial learning
    multiple times unless the student needs additional
    explanation or practice.

14. Once a topic has been introduced, prefer practice,
    revision, or mock tests for subsequent sessions.

15. Distribute study sessions across subjects according
    to their exam dates, difficulty, and preparation level.

16. Avoid repeatedly scheduling generic tasks when
    specific supplied topics are available.

OUTPUT REQUIREMENTS:
IMPORTANT ARRAY RULES:

- The "days" field must be an array of day objects.
- Every element inside "days" must be a JSON object.
- Never insert empty strings, null values, or other
  primitive values inside the "days" array.
- Every day object must contain exactly "date" and "items".
- Every element inside "items" must be a valid session
  object or break object.
- Empty days must use "items": [], not an empty string.
- Do not use blank strings as separators between objects.


Return ONLY valid JSON.

Do not include Markdown code fences, explanations,
or text outside the JSON object.

Use exactly this structure:

{{
  "schema_version": "1.0",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "items": [
        {{
          "kind": "session",
          "subject": "Subject name",
          "session_type": "learning",
          "task": "Description of the task",
          "topics": [],
          "duration_minutes": 60
        }},
        {{
          "kind": "break",
          "duration_minutes": 15
        }}
      ]
    }}
  ]
}}

Allowed session_type values:
- learning
- practice
- revision
- mock_test

Every item must have kind "session" or "break".

The latest exam date is {latest_exam_date}.
"""

    return prompt
