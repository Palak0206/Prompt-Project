
import json

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.input_models import StudentInput
from app.services.prompt_builder import build_timetable_prompt


api = Blueprint("api", __name__)


@api.post("/api/validate-input")
def validate_input():

    data = request.get_json(silent=True)

    # Check whether the request contains JSON
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain a valid JSON object."
        }), 400

    try:
        student = StudentInput.model_validate(data)

    except ValidationError as exc:
        return jsonify({
            "error": "Input validation failed.",
            "details": json.loads(exc.json(include_url=False))
        }), 400

    return jsonify({
        "message": "Student input is valid.",
        "student": student.model_dump(mode="json")
    }), 200
@api.post("/api/preview-prompt")
def preview_prompt():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain a valid JSON object."
        }), 400

    try:
        student = StudentInput.model_validate(data)

    except ValidationError as exc:
        return jsonify({
            "error": "Input validation failed.",
            "details": json.loads(exc.json(include_url=False))
        }), 400

    prompt = build_timetable_prompt(student)

    return jsonify({
        "message": "Prompt generated successfully.",
        "prompt": prompt
    }), 200
