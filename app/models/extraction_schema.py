
STUDENT_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "start_date": {
            "type": ["string", "null"],
            "description": "Study plan start date in YYYY-MM-DD format."
        },
        "max_daily_hours": {
            "type": ["number", "null"],
            "description": "Maximum number of hours the student can study per day."
        },
        "subjects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "exam_date": {
                        "type": ["string", "null"],
                        "description": "Exam date in YYYY-MM-DD format."
                    },
                    "difficulty": {
                        "type": ["string", "null"],
                        "enum": ["easy", "medium", "hard", None]
                    },
                    "preparation_percentage": {
                        "type": ["integer", "null"]
                    },
                    "topics": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name",
                    "exam_date",
                    "difficulty",
                    "preparation_percentage",
                    "topics"
                ],
                "additionalProperties": False
            }
        },
        "max_session_duration_minutes": {
            "type": ["integer", "null"]
        }
    },
    "required": [
        "start_date",
        "max_daily_hours",
        "subjects",
        "max_session_duration_minutes"
    ],
    "additionalProperties": False
}
