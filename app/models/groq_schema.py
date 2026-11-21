
TIMETABLE_GROQ_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_version": {
            "type": "string",
            "enum": ["1.0"]
        },
        "days": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string"
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "anyOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "kind": {
                                            "type": "string",
                                            "enum": ["session"]
                                        },
                                        "subject": {
                                            "type": "string"
                                        },
                                        "session_type": {
                                            "type": "string",
                                            "enum": [
                                                "learning",
                                                "practice",
                                                "revision",
                                                "mock_test"
                                            ]
                                        },
                                        "task": {
                                            "type": "string"
                                        },
                                        "topics": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "duration_minutes": {
                                            "type": "integer"
                                        }
                                    },
                                    "required": [
                                        "kind",
                                        "subject",
                                        "session_type",
                                        "task",
                                        "topics",
                                        "duration_minutes"
                                    ],
                                    "additionalProperties": False
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "kind": {
                                            "type": "string",
                                            "enum": ["break"]
                                        },
                                        "duration_minutes": {
                                            "type": "integer"
                                        }
                                    },
                                    "required": [
                                        "kind",
                                        "duration_minutes"
                                    ],
                                    "additionalProperties": False
                                }
                            ]
                        }
                    }
                },
                "required": ["date", "items"],
                "additionalProperties": False
            }
        }
    },
    "required": ["schema_version", "days"],
    "additionalProperties": False
}
