
import json

from pydantic import ValidationError

from app.models.input_models import StudentInput
from app.models.output_models import TimetableOutput

from app.services.prompt_builder import build_timetable_prompt
from app.services.groq_service import generate_timetable_response

from app.validators.timetable_validator import validate_timetable


MAX_GENERATION_ATTEMPTS = 2


class TimetableGenerationError(Exception):
    """Raised when timetable generation fails."""


def generate_timetable(student: StudentInput) -> TimetableOutput:

    # Build the original prompt once
    original_prompt = build_timetable_prompt(student)

    # This prompt may change after a failed attempt
    current_prompt = original_prompt

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):

        # 1. Generate response using Groq
        response_text = generate_timetable_response(current_prompt)

        errors = []

        # 2. Parse JSON
        try:
            response_data = json.loads(response_text)

        except json.JSONDecodeError:
            errors.append("Groq returned invalid JSON.")

        else:

            # 3. Validate output structure
            try:
                timetable = TimetableOutput.model_validate(response_data)

            except ValidationError as exc:
                errors.append(
                    f"Invalid timetable structure: {exc}"
                )

            else:

                # 4. Validate scheduling constraints
                errors = validate_timetable(timetable, student)

                # 5. Return only a valid timetable
                if not errors:
                    return timetable

        # 6. If the final attempt failed, stop
        if attempt == MAX_GENERATION_ATTEMPTS:
            raise TimetableGenerationError(
                f"Timetable remained invalid after "
                f"{MAX_GENERATION_ATTEMPTS} attempts. "
                + " ".join(errors)
            )

        # 7. Give Groq specific correction instructions
        current_prompt = f"""
{original_prompt}

CORRECTION REQUEST:

Your previous timetable was rejected by the Python validator.

The following errors were detected:

{chr(10).join(f"- {error}" for error in errors)}

Generate a completely corrected timetable.

IMPORTANT:
- Fix every error listed above.
- Follow the original student information and constraints.
- Do not change the required JSON structure.
- Return the complete timetable, not just the corrected parts.
- Return valid JSON only.
"""

    # Defensive fallback
    raise TimetableGenerationError(
        "Timetable generation failed unexpectedly."
    )
