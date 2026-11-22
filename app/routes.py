
import json
import logging

from flask import Blueprint, request, jsonify, render_template
from pydantic import ValidationError

from app.models.input_models import StudentInput
from app.services.extraction_service import extract_student_details
from app.services.prompt_builder import build_timetable_prompt
from app.services.timetable_service import (
    generate_timetable,
    TimetableGenerationError
)


api = Blueprint("api", __name__)


# ==============================
# 1. Homepage
# ==============================

@api.route("/")
def home():
    return render_template("index.html")


# ==============================
# 2. Extract Student Details
# ==============================

@api.post("/api/extract-student-details")
def extract_student_details_route():

    data = request.get_json(silent=True)

    # Check incoming JSON
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain a valid JSON object."
        }), 400

    query = data.get("query")

    # Check natural-language input
    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "error": "Please provide a valid study planning description."
        }), 400

    # Extract details using Groq
    try:
        extracted_data = extract_student_details(query.strip())

    except Exception:
        logging.exception("Student information extraction failed")

        return jsonify({
            "error": "Unable to extract student details. Please try again."
        }), 502

    return jsonify({
        "message": "Student details extracted successfully.",
        "extracted_data": extracted_data
    }), 200


# ==============================
# 3. Validate Student Input
# ==============================

@api.post("/api/validate-input")
def validate_input():

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

    return jsonify({
        "message": "Student input is valid.",
        "student": student.model_dump(mode="json")
    }), 200


# ==============================
# 4. Preview Generated Prompt
# ==============================

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


# ==============================
# 5. Generate Timetable
# ==============================

@api.post("/api/generate-timetable")
def generate_timetable_route():

    data = request.get_json(silent=True)

    # Check incoming JSON
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain a valid JSON object."
        }), 400

    # Validate student input
    try:
        student = StudentInput.model_validate(data)

    except ValidationError as exc:
        return jsonify({
            "error": "Input validation failed.",
            "details": json.loads(exc.json(include_url=False))
        }), 400

    # Generate and validate timetable
    try:
        timetable = generate_timetable(student)

    except TimetableGenerationError as exc:
        return jsonify({
            "error": "Timetable generation failed.",
            "details": str(exc)
        }), 422

    except Exception:
        logging.exception("Unexpected timetable generation error")

        return jsonify({
            "error": "An unexpected error occurred while generating the timetable."
        }), 502

    # Return validated timetable
    return jsonify({
        "message": "Timetable generated successfully.",
        "timetable": timetable.model_dump(mode="json")
    }), 200
